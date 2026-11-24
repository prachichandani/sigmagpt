
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router as chat_router
from routes.documents import router as documents_router
from ai.reranker import get_reranker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the cross-encoder once at startup so the first chat isn't slow
    try:
        get_reranker()
        logger.info("Reranker model loaded")
    except Exception:
        logger.exception("Could not preload reranker; it will retry on first RAG request")
    yield


app = FastAPI(lifespan=lifespan)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sigmagpt-phi.vercel.app","http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(documents_router)

