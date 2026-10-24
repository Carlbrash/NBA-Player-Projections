import pytest
from app.projection_batch import generate_upcoming

def test_rejects_invalid_window():
    with pytest.raises(ValueError):
        generate_upcoming(None,0)
    with pytest.raises(ValueError):
        generate_upcoming(None,169)
