import requests
import xml.etree.ElementTree as ET
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

class PubMedClient:
    """Client for querying PubMed via NCBI E-utilities with enriched provenance parsing."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    def __init__(self, email: str = "researcher@example.com", tool: str = "white_spot_analyzer"):
        self.email = email
        self.tool = tool
        self.rate_limit_delay = 0.4  # Max 3 requests per second without API key

    def search(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search PubMed and return a list of publication metadata."""
        pmids = self._get_pmids(query, max_results)
        if not pmids:
            return []
        
        return self._fetch_details(pmids)

    def get_by_pmids(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """Fetch details directly for a list of known PMIDs."""
        if not pmids:
            return []
        return self._fetch_details(pmids)

    def _get_pmids(self, query: str, max_results: int) -> List[str]:
        """Fetch PMIDs for a given query."""
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "email": self.email,
            "tool": self.tool
        }
        
        try:
            response = requests.get(self.BASE_URL + "esearch.fcgi", params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            return data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            print(f"[PubMed] Keresési hiba: {e}")
            return []

    def _fetch_details(self, pmids: List[str], batch_size: int = 100) -> List[Dict[str, Any]]:
        """Fetch XML details for PMIDs in batches."""
        publications = []
        total_batches = (len(pmids) + batch_size - 1) // batch_size

        for batch_num in range(total_batches):
            start = batch_num * batch_size
            end = start + batch_size
            batch = pmids[start:end]

            params = {
                "db": "pubmed",
                "id": ",".join(batch),
                "retmode": "xml",
                "rettype": "abstract",
                "email": self.email,
                "tool": self.tool
            }

            try:
                response = requests.get(self.BASE_URL + "efetch.fcgi", params=params, timeout=30)
                response.raise_for_status()
                publications.extend(self._parse_xml(response.text))
            except Exception as e:
                print(f"[PubMed] Letöltési hiba batch {batch_num}: {e}")

            time.sleep(self.rate_limit_delay)

        return publications

    def _parse_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parse PubMed XML response extracting enriched metadata including authors."""
        publications = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            print(f"[PubMed] XML Parse hiba: {e}")
            return []

        for article in root.findall(".//PubmedArticle"):
            pub: Dict[str, Any] = {"source": "PubMed"}
            
            # PMID
            pmid_el = article.find(".//PMID")
            pub["id"] = pmid_el.text if pmid_el is not None else ""
            
            # Title
            title_el = article.find(".//ArticleTitle")
            pub["title"] = "".join(title_el.itertext()).strip() if title_el is not None else ""
            
            # Authors extraction (LastName Initials)
            authors = []
            for author_el in article.findall(".//MedlineCitation/Article/AuthorList/Author"):
                last_name = author_el.findtext("LastName")
                initials = author_el.findtext("Initials")
                if last_name:
                    if initials:
                        authors.append(f"{last_name} {initials}")
                    else:
                        authors.append(last_name)
            pub["authors"] = authors
            if len(authors) > 1:
                pub["author_display"] = f"{authors[0]} et al."
            elif len(authors) == 1:
                pub["author_display"] = authors[0]
            else:
                pub["author_display"] = ""

            # Abstract
            abstract_texts = article.findall(".//AbstractText")
            if abstract_texts:
                abstract_parts = []
                for at in abstract_texts:
                    label = at.get("Label", "")
                    text = "".join(at.itertext()).strip() if at.text is not None or len(at) > 0 else ""
                    if label:
                        abstract_parts.append(f"{label}: {text}")
                    else:
                        abstract_parts.append(text)
                pub["abstract"] = " ".join(abstract_parts)
            else:
                pub["abstract"] = ""
                
            # Year
            year_el = article.find(".//PubDate/Year")
            if year_el is None:
                date_el = article.find(".//PubDate/MedlineDate")
                if date_el is not None and date_el.text:
                    pub["year"] = date_el.text[:4]
                else:
                    pub["year"] = ""
            else:
                pub["year"] = year_el.text or ""
                
            # Journal Title
            journal_el = article.find(".//Journal/Title")
            pub["journal"] = "".join(journal_el.itertext()).strip() if journal_el is not None else ""

            # DOI & PMCID
            pub["doi"] = ""
            pub["pmcid"] = None
            for id_el in article.findall(".//ArticleId"):
                id_type = id_el.get("IdType")
                if id_type == "doi" and not pub["doi"]:
                    pub["doi"] = id_el.text or ""
                elif id_type == "pmc" and not pub["pmcid"]:
                    pub["pmcid"] = id_el.text or None

            # Publication Types
            pub_types = []
            for pt in article.findall(".//MedlineCitation/Article/PublicationTypeList/PublicationType"):
                if pt.text:
                    pub_types.append(pt.text.strip())
            pub["publication_types"] = pub_types

            # Mesh Headings (Descriptors + Qualifiers)
            mesh_headings = []
            for mh in article.findall(".//MedlineCitation/MeshHeadingList/MeshHeading"):
                desc_el = mh.find("DescriptorName")
                if desc_el is not None and desc_el.text:
                    desc_text = desc_el.text.strip()
                    desc_ui = desc_el.get("UI", "")
                    is_major = desc_el.get("MajorTopicYN", "N") == "Y"
                    qualifiers = []
                    for q in mh.findall("QualifierName"):
                        if q.text:
                            qualifiers.append({
                                "qualifier": q.text.strip(),
                                "ui": q.get("UI", ""),
                                "is_major": q.get("MajorTopicYN", "N") == "Y"
                            })
                    mesh_headings.append({
                        "descriptor": desc_text,
                        "ui": desc_ui,
                        "is_major": is_major,
                        "qualifiers": qualifiers
                    })
            pub["mesh_headings"] = mesh_headings

            # Author Keywords
            author_keywords = []
            for kw in article.findall(".//MedlineCitation/KeywordList/Keyword"):
                kw_text = "".join(kw.itertext()).strip()
                if kw_text:
                    author_keywords.append({
                        "keyword": kw_text,
                        "is_major": kw.get("MajorTopicYN", "N") == "Y"
                    })
            pub["author_keywords"] = author_keywords

            # Retrieval Metadata
            timestamp_str = datetime.now(timezone.utc).isoformat()
            pub["retrieval_metadata"] = {
                "timestamp": timestamp_str,
                "has_mesh": len(mesh_headings) > 0,
                "has_oa_pmc": pub["pmcid"] is not None
            }

            publications.append(pub)

        return publications

    def fetch_pmc_xml(self, pmcid: str) -> Optional[str]:
        """Fetch PMC Open Access XML for a given PMCID."""
        if not pmcid:
            return None
        
        clean_id = pmcid.strip()
        params = {
            "db": "pmc",
            "id": clean_id,
            "retmode": "xml",
            "email": self.email,
            "tool": self.tool
        }
        
        try:
            time.sleep(self.rate_limit_delay)
            resp = requests.get(self.BASE_URL + "efetch.fcgi", params=params, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"[PubMed/PMC] Hiba a {clean_id} letöltésekor: {e}")
            return None

    def determine_provenance_tier(self, publication: Dict[str, Any], check_pmc_oa: bool = True) -> Dict[str, Any]:
        """
        Determine search key provenance tier based on the canonical 3-tier hierarchy:
        - Gold: Cochrane Appendix 1 (CSAK akkor, ha a PMC full-text XML-ben TÉNYLEGESEN azonosítható az Appendix 1 / teljes szintaxis)
                VAGY PMC OA XML-ből kinyert keresési stratégia / appendix szekció.
        - Silver: MEDLINE MeSH Record (<MeshHeadingList> vagy Author Keywords).
                  Ide minősül vissza a Cochrane cikk is, ha az Appendix 1 hiányzik a PMC XML-ből!
        - Bronze: Kizárólag Cím és Absztrakt szövege.
        """
        journal = (publication.get("journal") or "").lower()
        source = (publication.get("source") or "").lower()
        pmcid = publication.get("pmcid")
        mesh_headings = publication.get("mesh_headings") or []
        keywords = publication.get("author_keywords") or []

        is_cochrane = ("cochrane database of systematic reviews" in journal or 
                       "cochrane database syst rev" in journal or 
                       source == "cochrane")

        # 1. Ha van PMCID és engedélyezett a PMC OA vizsgálat:
        if pmcid and check_pmc_oa:
            pmc_xml = self.fetch_pmc_xml(pmcid)
            if pmc_xml:
                try:
                    root = ET.fromstring(pmc_xml)
                    search_keywords = ["search strategy", "search methods", "literature search", "appendix 1", "data sources", "electronic search"]
                    
                    for sec in root.findall(".//sec"):
                        title_el = sec.find("title")
                        if title_el is not None and title_el.text:
                            sec_title = "".join(title_el.itertext()).strip()
                            sec_title_lower = sec_title.lower()
                            
                            if any(k in sec_title_lower for k in search_keywords):
                                full_text = "".join(sec.itertext()).strip()
                                cleaned_text = " ".join(full_text.split())
                                
                                if is_cochrane:
                                    # Szigorú Cochrane igazolás: van-e tényleges Appendix 1 vagy raw Boole-szintaxis
                                    is_real_appendix = "appendix" in sec_title_lower
                                    has_raw_boolean_syntax = any(term in cleaned_text.lower() for term in ["\" or \"", "\" and \"", "exp ", "[tiab]", "mesh heading", "#1 and #2", "1 and 2"])
                                    
                                    if is_real_appendix or has_raw_boolean_syntax:
                                        return {
                                            "tier": "Gold",
                                            "provenance_label": "[Source: Cochrane Appendix 1]",
                                            "source_type": "Cochrane Systematic Review",
                                            "description": f"Cochrane Review Appendix 1 igazolva: '{sec_title}' ({pmcid})",
                                            "search_strategy_snippet": cleaned_text[:350],
                                            "verified_pmcid": pmcid
                                        }
                                    # Ha csak a rövid narratív összefoglaló szerepel (pl. PMC7003568) -> vissza kell esnie Silverre!
                                    break
                                else:
                                    # Normál PMC OA cikk kinyert szekcióval:
                                    return {
                                        "tier": "Gold",
                                        "provenance_label": "[Source: Full-Text Appendix]",
                                        "source_type": "PMC Open Access Full-Text",
                                        "description": f"PMC Open Access szekció '{sec_title}' azonosítva ({pmcid})",
                                        "search_strategy_snippet": cleaned_text[:350],
                                        "verified_pmcid": pmcid
                                    }
                except ET.ParseError:
                    print(f"[PubMed/PMC] Figyelem: {pmcid} XML parszolása sikertelen.")

        # 2. Silver Standard (MEDLINE MeSH és Szerzői Kulcsszavak)
        if mesh_headings or keywords:
            desc_count = len(mesh_headings)
            kw_count = len(keywords)
            major_descriptors = [m["descriptor"] for m in mesh_headings if m.get("is_major")]
            
            if is_cochrane:
                description = "Cochrane cikk, de az Appendix 1 tartalom automatikusan nem volt kinyerhető (PMC XML-ből hiányzik) — kézi ellenőrzés javasolt"
                snippet = f"(Cochrane Appendix 1 hiányzik a PMC-ből; MeSH lista: {', '.join(major_descriptors[:4]) if major_descriptors else ', '.join(m['descriptor'] for m in mesh_headings[:4])})"
            else:
                description = f"MEDLINE MeSH rekord ({desc_count} deskriptor, {kw_count} kulcsszó)"
                snippet = f"Major MeSH: {', '.join(major_descriptors[:5])}" if major_descriptors else f"MeSH: {', '.join(m['descriptor'] for m in mesh_headings[:5])}"

            return {
                "tier": "Silver",
                "provenance_label": "[Source: MEDLINE MeSH Record]",
                "source_type": "NLM MEDLINE Curated Record",
                "description": description,
                "search_strategy_snippet": snippet,
                "verified_pmcid": pmcid
            }

        # 3. Bronze Standard Fallback (Cím és Absztrakt)
        return {
            "tier": "Bronze",
            "provenance_label": "[Source: Title/Abstract Text]",
            "source_type": "Title & Abstract NLP Mining",
            "description": "Kizárólag Cím és Absztrakt szövege (nem indexelt / nyers)",
            "search_strategy_snippet": None,
            "verified_pmcid": pmcid
        }

    def enrich_with_provenance(self, publications: List[Dict[str, Any]], check_pmc_oa: bool = True) -> List[Dict[str, Any]]:
        """Add provenance metadata to each publication in the list."""
        enriched = []
        for pub in publications:
            pub_copy = dict(pub)
            pub_copy["provenance"] = self.determine_provenance_tier(pub_copy, check_pmc_oa=check_pmc_oa)
            enriched.append(pub_copy)
        return enriched

    def format_precedent_table(self, publications_with_provenance: List[Dict[str, Any]]) -> str:
        """Format an enriched precedent list as a CTM canonical Markdown table."""
        lines = [
            "| # | Szerző, Év | PMID | Cím | PMCID | Provenance Szint | Kinyert Kifejezések / Szintaxis |",
            "|:---:|---|:---:|---|:---:|:---:|---|"
        ]

        for idx, pub in enumerate(publications_with_provenance, 1):
            pmid = pub.get("id", "-")
            pmid_link = f"[{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid})" if pmid != "-" else "-"
            title = pub.get("title", "No Title")
            year = pub.get("year", "")
            
            # Author display formatting (e.g. "Jacobs SE et al., 2013")
            author_disp = pub.get("author_display", "")
            if author_disp and year:
                author_str = f"{author_disp}, {year}"
            elif author_disp:
                author_str = author_disp
            elif year:
                author_str = f"Study ({year})"
            else:
                author_str = f"Pubmed #{pmid}"

            pmcid = pub.get("pmcid") or "-"
            prov = pub.get("provenance") or {}
            prov_label = prov.get("provenance_label", "[Source: Title/Abstract Text]")
            
            # Summary of extracted terms
            extracted_parts = []
            if prov.get("search_strategy_snippet"):
                extracted_parts.append(prov["search_strategy_snippet"])
            elif pub.get("mesh_headings"):
                top_mesh = [m["descriptor"] for m in pub["mesh_headings"] if m.get("is_major")][:3]
                if not top_mesh:
                    top_mesh = [m["descriptor"] for m in pub["mesh_headings"][:3]]
                extracted_parts.append(", ".join(f'"{m}"[MeSH]' for m in top_mesh))
            elif pub.get("author_keywords"):
                top_kw = [k["keyword"] for k in pub["author_keywords"][:3]]
                extracted_parts.append(", ".join(top_kw))
            else:
                extracted_parts.append("Absztrakt szöveges szinonimák")

            extracted_str = " ".join(extracted_parts)[:120]
            safe_title = title[:65].replace("|", "/")
            safe_extracted = extracted_str.replace("|", "/")

            lines.append(f"| {idx} | **{author_str}** | {pmid_link} | *{safe_title}...* | {pmcid} | `{prov_label}` | {safe_extracted} |")

        return "\n".join(lines)
