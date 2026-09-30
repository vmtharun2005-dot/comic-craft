from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from models.gemini_flash import generate_outline
from models.gemini_pro import generate_story
from models.image_generator import generate_image
from models.layout_builder import build_comic_layout
from models.exporters import save_pdf


router = APIRouter()

templates = Jinja2Templates(directory="models/templates")

# =========================================================
# HOME
# =========================================================

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


# =========================================================
# GENERATE COMIC
# =========================================================

@router.post("/generate")
async def generate_comic(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form("Alex"),
    setting: str = Form("forest"),
    tone: str = Form("adventurous"),
    art_style: str = Form("anime"),
):

    try:

        # -------------------------------------------------
        # STEP 1 - Generate outline
        # -------------------------------------------------

        outline = generate_outline(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        # -------------------------------------------------
        # STEP 2 - Generate story
        # -------------------------------------------------

        story = generate_story(
    outline,
    character_name,
    setting,
    tone
)

        # -------------------------------------------------
        # STEP 3 - Generate images
        # -------------------------------------------------

        image_paths = []

        for panel in outline:

            if isinstance(panel, dict):
                image_prompt = panel.get(
                    "image_prompt",
                    panel.get(
                        "scene_description",
                        story_prompt
                    )
                )
            else:
                image_prompt = str(panel)

            image_path = generate_image(
                image_prompt,
                art_style
            )

            image_paths.append(image_path)

        # -------------------------------------------------
        # STEP 4 - Build comic layout
        # -------------------------------------------------

        layout = build_comic_layout(
            outline,
            story,
            image_paths
        )

        if not layout:
            raise ValueError(
                "The AI could not generate a valid comic layout."
            )

        # -------------------------------------------------
        # STEP 5 - Save PDF
        # -------------------------------------------------

        pdf_url = save_pdf(
            layout,
            character_name
        )

        # -------------------------------------------------
        # STEP 6 - Preview
        # -------------------------------------------------

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "request": request,
                "layout": layout,
                "character_name": character_name,
                "pdf_url": pdf_url,
            }
        )

    except Exception as exc:

        print(f"Generate route error: {exc}")

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": str(exc),
            },
            status_code=400,
        )


# =========================================================
# EXPORT SUCCESS
# =========================================================

@router.get("/export-success")
async def export_success(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "request": request
        }
    )


# =========================================================
# HEALTH
# =========================================================

@router.get("/health")
async def health():

    return {
        "status": "ok",
        "message": "ComicCraft API is running"
    }