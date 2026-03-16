import tkinter as tk

MAU = {
    "nen_chinh": "#0B0D10",
    "nen_dau_trang": "#111317",
    "nen_nut": "#111317",
    "nen_nut_chinh": "#1F6FEB",
    "nen_nut_chinh_hover": "#1A5DD0",
    "nen_nhap": "#2A2F36",
    "nen_bong_toi": "#F3E7D8",
    "nen_bong_khac": "#1C6AE0",
    "vien_phan_cach": "#0B0D10",
    "chu_trang": "white",
    "chu_phu": "#B6BCC6",
    "chu_toi": "#111827",
    "chu_ten_toi": "#C9A37B",
}

FONT = {
    "tieu_de": ("Segoe UI", 13, "bold"),
    "trang_thai": ("Segoe UI", 9),
    "chu_bong": ("Segoe UI", 11),
    "chu_ten": ("Segoe UI", 9, "bold"),
    "chu_gio": ("Segoe UI", 8),
    "nut_dau_trang": ("Segoe UI", 11),
    "nut_cong_cu": ("Segoe UI", 10, "normal"),
    "nut_gif": ("Segoe UI", 10, "bold"),
    "nut_phan_nhap": ("Segoe UI", 11, "bold"),
    "o_nhap": ("Segoe UI", 11),
    "avatar": ("Segoe UI", 12, "bold"),
}


def cau_hinh_cua_so(cua_so: tk.Tk) -> None:
    cua_so.title("Hệ thống chat server")
    cua_so.geometry("520x720")
    cua_so.configure(bg=MAU["nen_chinh"])


def cap_nhat_avatar(app) -> None:
    canvas = getattr(app, "avatar_canvas", None)
    if canvas is None:
        return
    canvas.delete("all")

    anh = getattr(app, "avatar_image", None)
    if anh is not None:
        canvas.create_image(21, 21, image=anh)
        return

    mau = getattr(app, "avatar_color", MAU["nen_nut_chinh"])
    chu_cai = (getattr(app, "biet_danh", "A")[:1] or "A").upper()
    canvas.create_oval(2, 2, 40, 40, fill=mau, outline="")
    canvas.create_text(21, 21, text=chu_cai, fill=MAU["chu_trang"], font=FONT["avatar"])


def tao_dau_trang(app) -> None:
    dau_trang = tk.Frame(app.cua_so, bg=MAU["nen_dau_trang"])
    dau_trang.pack(fill="x")

    ben_trai = tk.Frame(dau_trang, bg=MAU["nen_dau_trang"])
    ben_trai.pack(side="left", padx=12, pady=12)

    app.avatar_canvas = tk.Canvas(
        ben_trai, width=42, height=42, bg=MAU["nen_dau_trang"], highlightthickness=0
    )
    app.avatar_canvas.pack(side="left")
    if hasattr(app, "doi_avatar"):
        app.avatar_canvas.bind("<Button-1>", lambda _e: app.doi_avatar())
    cap_nhat_avatar(app)

    hop_tieu_de = tk.Frame(ben_trai, bg=MAU["nen_dau_trang"])
    hop_tieu_de.pack(side="left", padx=10)

    tk.Label(
        hop_tieu_de,
        text=app.biet_danh,
        bg=MAU["nen_dau_trang"],
        fg=MAU["chu_trang"],
        font=FONT["tieu_de"],
    ).pack(anchor="w")

    hang_trang_thai = tk.Frame(hop_tieu_de, bg=MAU["nen_dau_trang"])
    hang_trang_thai.pack(anchor="w", pady=(2, 0))
    cham = tk.Canvas(
        hang_trang_thai,
        width=10,
        height=10,
        bg=MAU["nen_dau_trang"],
        highlightthickness=0,
    )
    cham.pack(side="left")
    cham.create_oval(2, 2, 8, 8, fill="#22C55E", outline="")
    tk.Label(
        hang_trang_thai,
        text="Đang hoạt động",
        bg=MAU["nen_dau_trang"],
        fg=MAU["chu_phu"],
        font=FONT["trang_thai"],
    ).pack(side="left", padx=(6, 0))

    ben_phai = tk.Frame(dau_trang, bg=MAU["nen_dau_trang"])
    ben_phai.pack(side="right", padx=10, pady=10)

    for text in ("\U0001f4de", "\U0001f3a5", "\u24d8"):
        tk.Button(
            ben_phai,
            text=text,
            command=lambda: None,
            bd=0,
            relief="flat",
            bg=MAU["nen_nut"],
            fg="#E7E7E7",
            activebackground=MAU["nen_nut"],
            activeforeground=MAU["chu_trang"],
            padx=8,
            pady=6,
            cursor="hand2",
            font=FONT["nut_dau_trang"],
        ).pack(side="left")

    tk.Frame(app.cua_so, bg=MAU["vien_phan_cach"], height=1).pack(fill="x")


def tao_khung_chat(app) -> None:
    khung = tk.Frame(app.cua_so, bg=MAU["nen_chinh"])
    khung.pack(fill="both", expand=True)

    app.khung_chat = tk.Canvas(khung, bg=MAU["nen_chinh"], highlightthickness=0, bd=0)
    app.khung_chat.pack(side="left", fill="both", expand=True)

    thanh_cuon = tk.Scrollbar(khung, orient="vertical", command=app.khung_chat.yview)
    thanh_cuon.pack(side="right", fill="y")
    app.khung_chat.configure(yscrollcommand=thanh_cuon.set)

    app.khung_tin_nhan = tk.Frame(app.khung_chat, bg=MAU["nen_chinh"])
    app._cua_so_tin_nhan = app.khung_chat.create_window(
        (0, 0), window=app.khung_tin_nhan, anchor="nw"
    )

    app.khung_tin_nhan.bind("<Configure>", app._cap_nhat_khung_tin)
    app.khung_chat.bind("<Configure>", app._cap_nhat_canvas)

    app.khung_chat.bind_all("<MouseWheel>", app._cuon_chuot)


def tao_phan_nhap(app) -> None:
    phan_nhap = tk.Frame(app.cua_so, bg=MAU["nen_dau_trang"])
    phan_nhap.pack(fill="x")

    bieu_tuong_trai = tk.Frame(phan_nhap, bg=MAU["nen_dau_trang"])
    bieu_tuong_trai.pack(side="left", padx=(10, 6), pady=10)

    for text in ("\U0001f3a4", "\U0001f5bc\ufe0f", "\U0001f3a8", "GIF"):
        tk.Button(
            bieu_tuong_trai,
            text=text,
            command=lambda: None,
            bd=0,
            relief="flat",
            bg=MAU["nen_dau_trang"],
            fg="#E7E7E7",
            activebackground=MAU["nen_dau_trang"],
            activeforeground=MAU["chu_trang"],
            padx=6,
            pady=4,
            cursor="hand2",
            font=FONT["nut_gif"] if text == "GIF" else FONT["nut_cong_cu"],
        ).pack(side="left")

    vien_nhap = tk.Frame(phan_nhap, bg=MAU["nen_nhap"], padx=1, pady=1)
    vien_nhap.pack(side="left", fill="x", expand=True, padx=(0, 6), pady=10)

    ruot_nhap = tk.Frame(vien_nhap, bg=MAU["nen_nhap"])
    ruot_nhap.pack(fill="both", expand=True)

    app.nhap = tk.Entry(
        ruot_nhap,
        bd=0,
        relief="flat",
        bg=MAU["nen_nhap"],
        fg="#E7E7E7",
        insertbackground="#E7E7E7",
        font=FONT["o_nhap"],
    )
    app.nhap.pack(padx=12, pady=10, fill="x", expand=True)
    app.nhap.bind("<Return>", lambda _event: app.gui())

    bieu_tuong_phai = tk.Frame(phan_nhap, bg=MAU["nen_dau_trang"])
    bieu_tuong_phai.pack(side="right", padx=(6, 10), pady=10)

    for text in ("\u263a", "\u2665"):
        tk.Button(
            bieu_tuong_phai,
            text=text,
            command=lambda: None,
            bd=0,
            relief="flat",
            bg=MAU["nen_dau_trang"],
            fg="#E7E7E7" if text == "Smile" else MAU["nen_nut_chinh"],
            activebackground=MAU["nen_dau_trang"],
            activeforeground=MAU["chu_trang"],
            padx=6,
            pady=4,
            cursor="hand2",
            font=FONT["nut_phan_nhap"],
        ).pack(side="left")

    app.nut_gui = tk.Button(
        bieu_tuong_phai,
        text="\u27a4",
        command=app.gui,
        bd=0,
        relief="flat",
        bg=MAU["nen_nut_chinh"],
        fg=MAU["chu_trang"],
        activebackground=MAU["nen_nut_chinh_hover"],
        activeforeground=MAU["chu_trang"],
        padx=10,
        pady=6,
        cursor="hand2",
        font=FONT["nut_phan_nhap"],
    )
    app.nut_gui.pack(side="left", padx=(6, 0))


def them_bong_tin(
    app, nguoi_gui: str, noi_dung: str, la_toi: bool, thoi_gian: str | None = None
) -> None:
    hang = tk.Frame(app.khung_tin_nhan, bg=MAU["nen_chinh"])
    hang.pack(fill="x", padx=12, pady=6)

    canh = "e" if la_toi else "w"
    nen_bong = MAU["nen_bong_toi"] if la_toi else MAU["nen_bong_khac"]
    mau_chu = MAU["chu_toi"] if la_toi else MAU["chu_trang"]
    mau_ten = MAU["chu_ten_toi"] if la_toi else MAU["chu_phu"]

    hop = tk.Frame(hang, bg=MAU["nen_chinh"])
    hop.pack(anchor=canh)

    if not la_toi:
        tk.Label(
            hop,
            text=nguoi_gui,
            bg=MAU["nen_chinh"],
            fg=mau_ten,
            font=FONT["chu_ten"],
        ).pack(anchor="w", pady=(0, 2))

    bong = tk.Label(
        hop,
        text=noi_dung,
        bg=nen_bong,
        fg=mau_chu,
        font=FONT["chu_bong"],
        justify="left",
        wraplength=340,
        padx=12,
        pady=10,
    )
    bong.pack(anchor=canh)

    if thoi_gian:
        tk.Label(
            hop,
            text=thoi_gian,
            bg=MAU["nen_chinh"],
            fg=MAU["chu_phu"],
            font=FONT["chu_gio"],
        ).pack(anchor=canh, pady=(4, 0))

    app.cua_so.after(0, lambda: app.khung_chat.yview_moveto(1.0))
