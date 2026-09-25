import fitz # PyMuPDF
from pptx import Presentation
from pptx.util import Inches, Pt
import os
import shutil

pdf_path = r"C:\Users\shuba\Desktop\Researcher - Dóri\Ábrák.pdf"
pptx_path = r"C:\Users\shuba\Desktop\Researcher - Dóri\Physiology_Presentation.pptx"
temp_dir = r"C:\Users\shuba\Desktop\Researcher - Dóri\temp_images"

# Open PDF and extract all pages as images
pdf_doc = fitz.open(pdf_path)
os.makedirs(temp_dir, exist_ok=True)
for i in range(len(pdf_doc)):
    page = pdf_doc.load_page(i)
    pix = page.get_pixmap(dpi=150)
    pix.save(os.path.join(temp_dir, f"page_{i+1}.png"))

prs = Presentation()
blank_slide_layout = prs.slide_layouts[6]
title_slide_layout = prs.slide_layouts[0]
bullet_slide_layout = prs.slide_layouts[1]

# Slide 1: Title Slide
slide = prs.slides.add_slide(title_slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "Metabolic and Thermoregulatory Responses to aMSH and Leptin"
subtitle.text = "Analysis of Normal Fed, Calorie Restricted, and Trained States\n\nSpeaker notes contain English and Hungarian scripts."
notes_slide = slide.notes_slide
text_frame = notes_slide.notes_text_frame
text_frame.text = "Welcome everyone. Today, I will present our findings on how the central melanocortin (aMSH) and leptin systems regulate metabolism and body temperature, and crucially, how this regulation changes based on the animal's nutritional and physical state.\n\nÜdvözlök mindenkit. Ma arról fogok beszélni, hogy a centrális melanocortin (aMSH) és leptin rendszerek hogyan szabályozzák az anyagcserét és a testhőmérsékletet, és ami a legfontosabb: hogyan változik ez a szabályozás az állat tápláltsági és fizikai állapota szerint."

# Helper to add a slide with multiple images
def add_custom_slide(title_text, image_pages, notes_text):
    slide = prs.slides.add_slide(blank_slide_layout)
    # Add title box
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(1))
    tf = txBox.text_frame
    p = tf.add_paragraph()
    p.text = title_text
    p.font.size = Pt(32)
    p.font.bold = True
    
    if len(image_pages) == 2:
        slide.shapes.add_picture(os.path.join(temp_dir, f"page_{image_pages[0]}.png"), Inches(0.5), Inches(2.0), width=Inches(4.2))
        slide.shapes.add_picture(os.path.join(temp_dir, f"page_{image_pages[1]}.png"), Inches(5.0), Inches(2.0), width=Inches(4.2))
    elif len(image_pages) == 5:
        # Top row: 2 images
        slide.shapes.add_picture(os.path.join(temp_dir, f"page_{image_pages[0]}.png"), Inches(1.0), Inches(1.2), width=Inches(3.8))
        slide.shapes.add_picture(os.path.join(temp_dir, f"page_{image_pages[1]}.png"), Inches(5.2), Inches(1.2), width=Inches(3.8))
        # Bottom row: 3 images
        slide.shapes.add_picture(os.path.join(temp_dir, f"page_{image_pages[2]}.png"), Inches(0.2), Inches(4.3), width=Inches(3.1))
        slide.shapes.add_picture(os.path.join(temp_dir, f"page_{image_pages[3]}.png"), Inches(3.4), Inches(4.3), width=Inches(3.1))
        slide.shapes.add_picture(os.path.join(temp_dir, f"page_{image_pages[4]}.png"), Inches(6.6), Inches(4.3), width=Inches(3.1))
    elif len(image_pages) == 1:
        slide.shapes.add_picture(os.path.join(temp_dir, f"page_{image_pages[0]}.png"), Inches(1.5), Inches(1.5), width=Inches(7.0))
        
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text

add_custom_slide(
    "Experimental Models / Kísérleti Modellek",
    [2, 3],
    "First, let's validate our models. We divided the animals into three groups: Normal Fed (NF), Calorie Restricted (CR), and physically Trained (TR). As you can see in the tables, our CR intervention was successful, resulting in significantly lower body weights (~400g) compared to the NF controls (~540g).\n\nElőször is nézzük a kísérleti modelljeinket. Az állatokat három csoportba osztottuk: normálisan táplált (NF), kalóriamegvonásos (CR) és fizikailag edzett (TR). Ahogy a táblázatok is mutatják, a CR intervenció sikeres volt: az állatok testtömege jelentősen alacsonyabb (~400g) volt az NF kontrollokhoz képest (~540g)."
)

add_custom_slide(
    "The Baseline aMSH Response (Normal Fed)",
    [13, 11, 12, 9, 10],
    "Let's start with aMSH in a healthy, Normal Fed state. aMSH significantly alters oxygen consumption (VO2), indicating a shift in energy expenditure. Consequently, this metabolic shift drives an increase in core body temperature (Tc). The Heat Loss Index (HLI) remains relatively flat.\n\nKezdjük az aMSH hatásával az egészséges, normálisan táplált (NF) állapotban. Az aMSH jelentősen megváltoztatja az oxigénfogyasztást (VO2). Ez a metabolikus változás a maghőmérséklet (Tc) emelkedéséhez vezet. A hőleadási index (HLI) viszonylag lapos marad."
)

add_custom_slide(
    "aMSH During Caloric Restriction (CR)",
    [8, 6, 7, 4, 5],
    "Now, what happens during starvation? In the CR group, the baseline VO2 and Tc are already suppressed. When we administer aMSH, we still see a robust hyperthermic response (ΔTc rises). However, look at the HLI graph—there is a massive, significant spike in heat loss.\n\nMi történik éhezés alatt? A CR csoportban az alap VO2 és a Tc is alacsonyabb. Amikor aMSH-t adunk, továbbra is robusztus hipertermiás választ látunk. Azonban nézzük meg a HLI ábrát: hatalmas, szignifikáns csúcsot látunk a hőleadásban."
)

add_custom_slide(
    "aMSH in the Trained State (TR)",
    [18, 16, 17, 14, 15],
    "In physically trained animals, the aMSH response is even more dramatic. We see a strong and sustained hyperthermia. Interestingly, the VO2 and HLI dynamics mirror the CR group to some extent, with a sharp initial increase in heat loss followed by sustained core heating.\n\nA fizikailag edzett állatoknál az aMSH válasz még drámaibb. Érdekes módon a VO2 és a HLI dinamikája bizonyos mértékig a CR csoporthoz hasonlít: kezdetben hirtelen megnő a hőleadás, amit tartós maghőmérséklet-emelkedés követ."
)

add_custom_slide(
    "Transition to Leptin",
    [19],
    "Having established how nutritional and physical states alter the melanocortin system, we next asked: does Leptin—a key satiety hormone—operate under the same thermal logic?\n\nMiután láttuk, hogyan módosítja a tápláltsági és fizikai állapot a melanocortin rendszert, a következő kérdésünk az volt: vajon a Leptin – a legfőbb jóllakottsági hormon – ugyanezen a termikus logikán alapulva működik?"
)

add_custom_slide(
    "Leptin Baseline Response (NF)",
    [29, 27, 28, 25, 26],
    "Looking at the Normal Fed animals, Leptin's effect is much more subtle compared to aMSH. The changes in VO2 and Tc are minimal, and the HLI shows no dramatic heat dissipation.\n\nA normálisan táplált állatoknál a Leptin hatása sokkal enyhébb az aMSH-hoz képest. A VO2 és a Tc változásai minimálisak, és a HLI sem mutat drámai hőleadást."
)

add_custom_slide(
    "Leptin During Caloric Restriction (CR)",
    [24, 22, 23, 20, 21],
    "In Calorie Restriction, the system is sensitized. Leptin essentially signals 'false satiety' to a starving brain. We see a modest, steady rise in Tc without the drastic heat loss (HLI) spike we saw with aMSH.\n\nKalóriamegvonás esetén a rendszer érzékennyé válik. A Leptin lényegében 'hamis jóllakottságot' jelez az éhező agynak. A Tc mérsékelt, folyamatos emelkedését látjuk, anélkül a drasztikus hőleadási (HLI) csúcs nélkül."
)

add_custom_slide(
    "Leptin in the Trained State (TR)",
    [34, 32, 33, 30, 31],
    "Finally, in the Trained group, the physiological separation between Leptin and aMSH becomes incredibly clear. While aMSH caused massive hyperthermia and an HLI spike, Leptin completely fails to elicit this intense response.\n\nVégül az edzett csoportban hihetetlenül világossá válik a Leptin és az aMSH közötti élettani különbség. Míg az aMSH masszív hipertermiát és HLI csúcsot okozott a TR állatoknál, a Leptin egyáltalán nem váltja ki ezt az intenzív választ."
)

# Slide 10: Conclusion
slide = prs.slides.add_slide(bullet_slide_layout)
shapes = slide.shapes
title_shape = shapes.title
body_shape = shapes.placeholders[1]
title_shape.text = "Summary / Összefoglalás"
tf = body_shape.text_frame
tf.text = "1. Nutritional deficiency (CR) and exercise adaptation (TR) fundamentally rewire how the brain responds to metabolic hormones."
p = tf.add_paragraph()
p.text = "2. aMSH induces hyperthermia across all states, but the mechanism of heat dissipation (HLI) is radically altered in energy deficit."
p = tf.add_paragraph()
p.text = "3. Exercise specifically sensitizes the melanocortin response while dampening acute leptin thermogenesis."

notes_slide = slide.notes_slide
text_frame = notes_slide.notes_text_frame
text_frame.text = "To summarize: 1. Both nutritional deficiency and exercise fundamentally rewire how the brain responds to metabolic hormones. 2. aMSH induces hyperthermia across all states, but the mechanism of heat dissipation is radically altered. 3. Exercise specifically sensitizes the melanocortin response while dampening acute leptin thermogenesis. Thank you for your attention.\n\nÖsszefoglalva: 1. Mind a táplálékhiány, mind az edzés adaptációja alapvetően átprogramozza az agy válaszát. 2. Az aMSH minden állapotban hipertermiát okoz, de a hőleadás mechanizmusa radikálisan megváltozik. 3. A fizikai edzés specifikusan érzékenyíti a melanocortin választ, miközben tompítja az akut leptin termogenezist. Köszönöm a figyelmet."

prs.save(pptx_path)

# cleanup temp images
shutil.rmtree(temp_dir)
print(f"Presentation saved successfully to {pptx_path}")
