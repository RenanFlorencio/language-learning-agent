from user_profile.schema import VideoInfo

mock_videos = [
    VideoInfo(
        video_id="3gmJXVqwiHQ",
        title=" 8 films pour améliorer ton français ",
        channel_id="UCcinema123",  # highly rated saved channel
        channel_title="Cinéma Facile",
        CC=True,
        published_time="1 month ago",
        views=85000,
        detected_language="French",
        detected_level="A2",      # perfect level match
        for_students=True,
        score=None
        # expected score: HIGHEST — cinema interest, saved channel,
        # perfect level, for students, CC available
    ),
    VideoInfo(
        video_id="Au7DPVUpc6A",
        title="La Révolution Française de 1789 à 1792 ",
        channel_id="UChistoire456",  # saved channel
        channel_title="Histoire Vivante",
        CC=True,
        published_time="3 months ago",
        views=120000,
        detected_language="French",
        detected_level="B1",      # slightly above target A2
        for_students=False,
        score=None
        # expected score: HIGH — history interest, saved channel
        # slight penalty for being above target level
    ),
    VideoInfo(
        video_id="Xu-FLmk7t5Y",
        title=" LA CUISINE FRANCAISE : C'EST SACRÉ ! ",
        channel_id="UCfood999",
        channel_title="Cuisine Française",
        CC=True,
        published_time="2 weeks ago",
        views=67000,
        detected_language="French",
        detected_level="A2",      # perfect level match
        for_students=False,
        score=None
        # expected score: MEDIUM-HIGH — gastronomy interest, right level
        # unknown channel, no ratings
    ),
    VideoInfo(
        video_id="dp4I9DIK_pk",
        title="Présidentielle 2022 : le débat entre Macron et Le Pen résumé en 6 minutes",
        channel_id="UCnews777",
        channel_title="France Info",
        CC=False,
        published_time="1 week ago",
        views=450000,
        detected_language="French",
        detected_level="C1",      # way above target
        for_students=False,
        score=None
        # expected score: LOW — not in interests, way above level,
        # no CC, not for students
    ),
    VideoInfo(
        video_id="2e7DAdOyb10",
        title="BAGARRES et INSULTES 😤 Les meilleurs moments ! | LES ANGES | COMPILATION",
        channel_id="UCreality789",  # poorly rated channel
        channel_title="Reality France",
        CC=False,
        published_time="2 days ago",
        views=1500000,
        detected_language="French",
        detected_level="B2",      # above target
        for_students=False,
        score=None
        # expected score: LOWEST — reality TV (disliked), poorly rated channel,
        # above level, no CC
    ),
]

mock_transcripts = {
    "3gmJXVqwiHQ": "Bonjour à tous ! Aujourd'hui je vous présente huit films pour améliorer votre français. Ces films sont parfaits pour les débutants. Les dialogues sont simples et clairs. Vous pouvez activer les sous-titres en français. Regarder des films est une excellente méthode pour apprendre une nouvelle langue naturellement.",
    
    "Au7DPVUpc6A": "La Révolution Française commence en 1789 avec la prise de la Bastille. Le peuple français était mécontent du roi Louis XVI. Les inégalités sociales étaient très importantes. Les idées des philosophes des Lumières ont influencé les révolutionnaires. Cette période a complètement transformé la société française et européenne.",
    
    "Xu-FLmk7t5Y": "La cuisine française est reconnue dans le monde entier comme un patrimoine culturel important. Aujourd'hui nous préparons un bœuf bourguignon traditionnel. Il faut du vin rouge, des carottes, des oignons et de la viande. La recette est simple mais demande beaucoup de patience et d'amour pour la gastronomie.",
    
    "dp4I9DIK_pk": "Ce débat présidentiel entre Emmanuel Macron et Marine Le Pen a été particulièrement tendu. Les deux candidats s'affrontent sur des questions économiques complexes, notamment concernant le pouvoir d'achat, la politique énergétique et les relations internationales. Les arguments échangés reflètent des visions diamétralement opposées de la société française contemporaine.",
    
    "2e7DAdOyb10": "Ouais nan mais là franchement il m'a cherché hein ! T'as vu comment il m'a regardé ? J'suis pas du genre à me laisser faire moi. Vas-y on s'explique dehors si t'as quelque chose à dire ! Les autres candidats de la villa essaient de calmer la situation mais ça dégénère rapidement."
}

