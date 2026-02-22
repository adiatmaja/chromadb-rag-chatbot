"""
Comprehensive retrieval test — covers ALL products, FAQs, and intents.

Products:  checks that the target SKU appears in the top-5 candidates
           (mirrors production: embedding → top-5 → LLM reranking)
FAQs:      checks that the correct FAQ id is the top-1 result
Intents:   checks that the correct intent_name is the top-1 result

Usage (Docker):
    PYTHONIOENCODING=utf-8 docker exec rag-product-search \
        python scripts/testing/test_all_retrieval.py

Usage (local):
    python scripts/testing/test_all_retrieval.py
"""

import os
import sys
from pathlib import Path

# ── path setup ──────────────────────────────────────────────────────────────
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent.parent))  # scripts/ for load_docker_compat

import load_docker_compat  # noqa: E402  (must run before chromadb)

if os.name == "nt":
    sys.stdout.reconfigure(encoding="utf-8")

# ── imports ──────────────────────────────────────────────────────────────────
from src.core.retriever import UnifiedRetriever  # noqa: E402


# ── test definitions ─────────────────────────────────────────────────────────

PRODUCT_TESTS = [
    # (query, expected_sku, label)
    ("indomie goreng",           "IMG001", "Indomie Mi Goreng Original"),
    ("indomie kuah",             "IMA002", "Indomie Mi Instan Ayam Bawang"),
    ("mie sedap goreng",         "MSG003", "Mie Sedaap Goreng Original"),
    ("le mineral",               "LMN004", "Le Minerale Air Mineral 600ml"),
    ("air aqua",                 "AQA005", "Aqua Air Mineral 600ml"),
    ("teh botol",                "TBS006", "Teh Botol Sosro Original"),
    ("kapal api mix",            "KKA007", "Kopi Kapal Api Special Mix"),
    ("gula rose brand",          "GGS008", "Gula Pasir Rose Brand 1kg"),
    ("susu bendera cokelat",     "SKM009", "Susu Kental Manis Frisian Flag Cokelat"),
    ("pocari sweat",             "PSS010", "Pocari Sweat 500ml"),
    ("sabun lifebuoy merah",     "SBR011", "Sabun Mandi Cair Lifebuoy"),
]

FAQ_TESTS = [
    # (query, expected_faq_id, label)
    ("cara melakukan pemesanan",                "1",  "Cara pemesanan"),
    ("minimum order berapa",                    "2",  "Minimum pemesanan"),
    ("metode pembayaran yang tersedia",         "3",  "Metode pembayaran"),
    ("berapa hari pengiriman",                  "4",  "Lama pengiriman"),
    ("ongkos kirim gratis",                     "5",  "Biaya pengiriman"),
    ("cara cek stok barang",                    "6",  "Cek stok produk"),
    ("harga bisa dinegosiasi",                  "7",  "Negosiasi harga"),
    ("barang rusak saat diterima",              "8",  "Produk rusak"),
    ("pesan produk di luar katalog",            "9",  "Produk non-katalog"),
    ("daftar jadi reseller",                    "10", "Mitra reseller"),
    ("program poin reward pelanggan",           "11", "Program loyalitas"),
    ("cara batalkan pesanan",                   "12", "Batalkan pesanan"),
    ("minta faktur pembelian",                  "13", "Faktur/nota"),
    ("produk paling laris",                     "14", "Produk terlaris"),
    ("cara pakai kode promo",                   "15", "Kode promo"),
]

INTENT_TESTS = [
    # (query, expected_intent_name, label)
    ("tambah 3 lagi ke keranjang",              "add_amount_of_item_in_cart",               "Tambah jumlah item"),
    ("mau pesan 2 dus indomie goreng",          "add_item_to_cart",                         "Tambah item ke cart"),
    ("mau tambah ke keranjang tapi belum pilih produknya", "add_item_to_cart_but_no_item_specified", "Pesan tanpa item"),
    ("pakai kode DISC20",                       "apply_promo_code",                         "Apply promo code"),
    ("jam operasional toko berapa",             "asking_general_questions",                 "Pertanyaan umum"),
    ("tampilkan katalog produk",                "asking_priority_products",                 "Lihat katalog"),
    ("berapa harga susu bendera",                "asking_specific_product",                  "Tanya produk spesifik"),
    ("tidak jadi beli, batalkan",               "cancel_adding_item_to_cart",               "Batal tambah item"),
    ("batalkan checkout",                       "cancel_checkout",                          "Batal checkout"),
    ("checkout sekarang",                       "checkout",                                 "Checkout"),
    ("terima kasih sampai jumpa",               "farewell_intent",                          "Farewell"),
    ("cek produk favorit saya",                 "favorite_product_stock_check_by_category", "Cek produk favorit"),
    ("halo selamat pagi",                       "greeting_intent",                          "Greeting"),
    ("tidak pakai promo",                       "not_applying_promo_code",                  "Tidak pakai promo"),
    ("berapa poin saya sekarang",               "question_about_customer_profile_points",   "Cek poin"),
    ("saya pelanggan prioritas bukan",          "question_about_customer_profile_priority", "Status prioritas"),
    ("kurangi 1 dari keranjang",                "reduce_amount_of_item_in_cart",            "Kurangi item"),
    ("lihat isi keranjang saya",                "view_cart",                                "Lihat keranjang"),
]


# ── helpers ──────────────────────────────────────────────────────────────────

def hr(char: str = "─", width: int = 70) -> str:
    return char * width


def run_products(retriever: UnifiedRetriever) -> tuple[int, int]:
    """Return (passed, total)."""
    print(f"\n{'═' * 70}")
    print("  PRODUCT RETRIEVAL  (target SKU must appear in top-5 candidates)")
    print(f"{'═' * 70}")

    passed = 0
    for query, expected_sku, label in PRODUCT_TESTS:
        candidates = retriever.get_product_candidates(query, n=5)
        found_skus = [c.metadata.get("sku") for c in candidates]
        ok = expected_sku in found_skus
        rank = found_skus.index(expected_sku) + 1 if ok else None
        top_score = candidates[0].relevance_score if candidates else 0.0

        status = "PASS" if ok else "FAIL"
        rank_str = f"rank #{rank}" if ok else "NOT IN TOP-5"
        print(f"  [{status}]  {label:<40}  query={query!r:<28}  {rank_str}  top_score={top_score:.3f}")
        if ok:
            passed += 1

    print(f"\n  Products: {passed}/{len(PRODUCT_TESTS)} passed")
    return passed, len(PRODUCT_TESTS)


def run_faqs(retriever: UnifiedRetriever) -> tuple[int, int]:
    """Return (passed, total)."""
    print(f"\n{'═' * 70}")
    print("  FAQ RETRIEVAL  (correct FAQ id must be top-1 result)")
    print(f"{'═' * 70}")

    passed = 0
    for query, expected_id, label in FAQ_TESTS:
        result = retriever.search(
            query,
            search_products=False,
            search_faqs=True,
            search_intents=False,
        )
        got_id = str(result.metadata.get("id", "")) if result else ""
        ok = got_id == expected_id
        score = result.relevance_score if result else 0.0

        status = "PASS" if ok else "FAIL"
        got_label = result.metadata.get("question", "none")[:50] if result else "none"
        print(f"  [{status}]  {label:<30}  query={query!r:<35}  got_id={got_id}  score={score:.3f}")
        if not ok:
            print(f"          expected id={expected_id}, got: {got_label!r}")
        if ok:
            passed += 1

    print(f"\n  FAQs: {passed}/{len(FAQ_TESTS)} passed")
    return passed, len(FAQ_TESTS)


def run_intents(retriever: UnifiedRetriever) -> tuple[int, int]:
    """Return (passed, total)."""
    print(f"\n{'═' * 70}")
    print("  INTENT CLASSIFICATION  (correct intent must be top-1 result)")
    print(f"{'═' * 70}")

    passed = 0
    for query, expected_intent, label in INTENT_TESTS:
        result = retriever.search(
            query,
            search_products=False,
            search_faqs=False,
            search_intents=True,
        )
        got_intent = result.metadata.get("intent_name", "") if result else ""
        ok = got_intent == expected_intent
        score = result.relevance_score if result else 0.0

        status = "PASS" if ok else "FAIL"
        print(f"  [{status}]  {label:<40}  query={query!r:<35}  score={score:.3f}")
        if not ok:
            print(f"          expected={expected_intent!r}, got={got_intent!r}")
        if ok:
            passed += 1

    print(f"\n  Intents: {passed}/{len(INTENT_TESTS)} passed")
    return passed, len(INTENT_TESTS)


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    print(hr("═"))
    print("  COMPREHENSIVE RETRIEVAL TEST")
    print(f"  Products={len(PRODUCT_TESTS)}  FAQs={len(FAQ_TESTS)}  Intents={len(INTENT_TESTS)}")
    print(hr("═"))

    # Suppress retriever's verbose output during batch runs by redirecting console
    # (UnifiedRetriever uses rich console.print, not logging — we capture nothing,
    # but the per-query rich output is intentionally skipped via a simple wrapper
    # that suppresses rich prints)
    import io
    from contextlib import redirect_stdout
    from rich.console import Console as RichConsole

    # Patch the module-level console to a null sink so rich output is silent
    import src.core.retriever as retriever_module
    null_console = RichConsole(file=io.StringIO(), highlight=False)
    original_console = retriever_module.console
    retriever_module.console = null_console

    try:
        retriever = UnifiedRetriever()
    except Exception as exc:
        retriever_module.console = original_console
        print(f"ERROR: Could not initialise UnifiedRetriever: {exc}")
        return 1

    p_pass, p_total = run_products(retriever)
    f_pass, f_total = run_faqs(retriever)
    i_pass, i_total = run_intents(retriever)

    retriever_module.console = original_console

    total_pass = p_pass + f_pass + i_pass
    total = p_total + f_total + i_total

    print(f"\n{hr('═')}")
    print(f"  SUMMARY")
    print(hr())
    print(f"  Products : {p_pass:2d}/{p_total}")
    print(f"  FAQs     : {f_pass:2d}/{f_total}")
    print(f"  Intents  : {i_pass:2d}/{i_total}")
    print(hr())
    print(f"  TOTAL    : {total_pass}/{total}  ({'PASS' if total_pass == total else 'FAIL'})")
    print(hr("═"))

    return 0 if total_pass == total else 1


if __name__ == "__main__":
    sys.exit(main())
