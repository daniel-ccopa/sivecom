from app.services.ocr.ocr_engine import parse_paddle_ocr_result


def test_parse_paddle_ocr_v3_result() -> None:
    raw_result = [
        {
            "res": {
                "rec_texts": ["ORDEN DE SERVICIO", "RUC 10426218131"],
                "rec_scores": [0.98, 0.87],
            }
        }
    ]

    lines = parse_paddle_ocr_result(raw_result)

    assert lines == [("ORDEN DE SERVICIO", 98.0), ("RUC 10426218131", 87.0)]


def test_parse_paddle_ocr_v2_result() -> None:
    raw_result = [
        [
            [[[0, 0], [10, 0], [10, 10], [0, 10]], ("Proveedor", 0.95)],
            [[[0, 20], [10, 20], [10, 30], [0, 30]], ["Monto Total", 0.91]],
        ]
    ]

    lines = parse_paddle_ocr_result(raw_result)

    assert lines == [("Proveedor", 95.0), ("Monto Total", 91.0)]
