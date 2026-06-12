import base64
import io
import logging

import matplotlib
matplotlib.use("Agg")  # non-interactive backend — required on servers without a display
import matplotlib.pyplot as plt

logger = logging.getLogger("mangodb.utils")


def fig_to_base64(fig) -> str:
    """Serialize a matplotlib Figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    try:
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        return encoded
    except Exception:
        logger.exception("Failed to serialize figure to base64")
        raise
    finally:
        plt.close(fig)
        buf.close()
