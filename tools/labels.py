"""Ten hien thi tieng Viet cho cac khoa (key) trong data/kpi_plan_2026.json."""

DEPARTMENT_NAMES = {
    "thiet_ke": "Phòng Thiết kế",
    "kinh_doanh": "Phòng Kinh doanh",
    "thi_cong": "Phòng Thi Công",
    "thi_cong_noi_that": "Phòng Thi Công Nội thất",
}

METRIC_NAMES = {
    "tong_doanh_thu": "Tổng doanh thu",
    "thiet_ke_noi_that": "Doanh thu thiết kế nội thất",
    "thiet_ke_kien_truc": "Doanh thu thiết kế kiến trúc",
    "san_luong_ky_thiet_ke": "Sản lượng ký thiết kế",
    "san_luong_ky_thiet_ke__sale1_nhu": "  - Sale 1 (Như)",
    "san_luong_ky_thiet_ke__sale2_hoang": "  - Sale 2 (Hoàng)",
    "san_luong_ky_thiet_ke__sale3": "  - Sale 3",
    "san_luong_ky_thiet_ke__sale4": "  - Sale 4",
    "san_luong_ky_thi_cong_tho": "Sản lượng ký thi công thô",
    "san_luong_ky_thi_cong_tho__sale1_nhu": "  - Sale 1 (Như)",
    "san_luong_ky_thi_cong_tho__sale2_hoang": "  - Sale 2 (Hoàng)",
    "san_luong_ky_thi_cong_tho__sale3": "  - Sale 3",
    "san_luong_ky_thi_cong_tho__sale4": "  - Sale 4",
    "san_luong_tc_hoan_thien": "Sản lượng TC hoàn thiện",
    "doanh_thu_tc_hoan_thien": "Doanh thu TC hoàn thiện",
    "san_luong_ky_tc_noi_that": "Sản lượng ký TC nội thất",
    "doanh_thu_tc_noi_that": "Doanh thu TC nội thất",
}

# Cac chi so "chinh" (khong phai breakdown theo sale) dung de cong don ra
# san luong / doanh thu toan cong ty, tranh dem trung phan breakdown.
COMPANY_SAN_LUONG_METRICS = [
    ("kinh_doanh", "san_luong_ky_thiet_ke"),
    ("kinh_doanh", "san_luong_ky_thi_cong_tho"),
    ("thi_cong", "san_luong_tc_hoan_thien"),
    ("thi_cong_noi_that", "san_luong_ky_tc_noi_that"),
]

COMPANY_DOANH_THU_METRICS = [
    ("thiet_ke", "tong_doanh_thu"),
    ("thi_cong", "doanh_thu_tc_hoan_thien"),
    ("thi_cong_noi_that", "doanh_thu_tc_noi_that"),
]

DOANH_THU_CAVEAT = (
    "Ke hoach KPI khong co lich trinh doanh thu rieng cho mang 'Thi cong tho' "
    "(chi co san luong ky hop dong), nen tong doanh thu cong don duoi day CHUA "
    "bao gom mang nay va se thap hon nhieu so voi muc tieu 77 ty ca nam."
)
