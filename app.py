
import streamlit as st
import pandas as pd
import html
import json

from pathlib import Path
from datetime import datetime
from utils.recommendations import recommend_books


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="BookFlix | Discover Your Next Read",
    page_icon="📚",
    layout="wide"
)


# ---------------- FILE PATHS ----------------

READING_LIST_FILE = Path("reading_list.json")
REVIEWS_FILE = Path("reviews.json")
PROFILE_FILE = Path("profile.json")


# ---------------- SESSION STATE ----------------

if "selected_book" not in st.session_state:
    st.session_state.selected_book = None

if "intro_shown" not in st.session_state:
    st.session_state.intro_shown = False


# ---------------- PROFILE FUNCTIONS ----------------

def load_profile():

    if not PROFILE_FILE.exists():
        return {"name": ""}

    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as file:
            profile = json.load(file)

        if isinstance(profile, dict):
            return {"name": str(profile.get("name", ""))}

        return {"name": ""}

    except (json.JSONDecodeError, ValueError, TypeError):
        return {"name": ""}


def save_profile(name):

    profile = {"name": name.strip()}

    with open(PROFILE_FILE, "w", encoding="utf-8") as file:
        json.dump(profile, file, indent=4, ensure_ascii=False)

    st.session_state.profile = profile


if "profile" not in st.session_state:
    st.session_state.profile = load_profile()


# ---------------- READING LIST FUNCTIONS ----------------

def load_reading_list():

    if not READING_LIST_FILE.exists():
        return []

    try:
        with open(READING_LIST_FILE, "r", encoding="utf-8") as file:
            saved_books = json.load(file)

        return [int(book_id) for book_id in saved_books]

    except (json.JSONDecodeError, ValueError, TypeError):
        return []


def save_reading_list(book_ids):

    with open(READING_LIST_FILE, "w", encoding="utf-8") as file:
        json.dump(book_ids, file, indent=4)


if "reading_list" not in st.session_state:
    st.session_state.reading_list = load_reading_list()


def add_to_reading_list(book_id):

    book_id = int(book_id)

    if book_id not in st.session_state.reading_list:
        st.session_state.reading_list.append(book_id)
        save_reading_list(st.session_state.reading_list)


def remove_from_reading_list(book_id):

    book_id = int(book_id)

    if book_id in st.session_state.reading_list:
        st.session_state.reading_list.remove(book_id)
        save_reading_list(st.session_state.reading_list)


# ---------------- RATING AND REVIEW FUNCTIONS ----------------

def load_reviews():

    if not REVIEWS_FILE.exists():
        return []

    try:
        with open(REVIEWS_FILE, "r", encoding="utf-8") as file:
            reviews = json.load(file)

        if isinstance(reviews, list):
            return reviews

        return []

    except (json.JSONDecodeError, ValueError, TypeError):
        return []


def save_reviews(reviews):

    with open(REVIEWS_FILE, "w", encoding="utf-8") as file:
        json.dump(reviews, file, indent=4, ensure_ascii=False)


if "reviews" not in st.session_state:
    st.session_state.reviews = load_reviews()


def add_review(book_id, rating, review_text):

    reviewer_name = st.session_state.profile.get("name", "").strip()

    if not reviewer_name:
        reviewer_name = "Reader"

    new_review = {
        "book_id": int(book_id),
        "name": reviewer_name,
        "rating": int(rating),
        "review": review_text.strip(),
        "date": datetime.now().strftime("%d %B %Y, %I:%M %p")
    }

    st.session_state.reviews.append(new_review)
    save_reviews(st.session_state.reviews)


def get_book_reviews(book_id):

    return [
        review
        for review in st.session_state.reviews
        if int(review.get("book_id", -1)) == int(book_id)
    ]


def get_review_statistics(book_id):

    book_reviews = get_book_reviews(book_id)

    if not book_reviews:
        return 0, 0

    average_rating = sum(
        int(review["rating"])
        for review in book_reviews
    ) / len(book_reviews)

    return round(average_rating, 1), len(book_reviews)


# ---------------- LOAD DATASET ----------------

@st.cache_data
def load_books():
    return pd.read_csv("data/books.csv")


books = load_books()


# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.stApp {
    background-color: #101010;
    color: white;
    font-family: 'Inter', Arial, sans-serif;
}

html, body, [class*="css"] {
    font-family: 'Inter', Arial, sans-serif;
}

header[data-testid="stHeader"] {
    background-color: #101010;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1300px;
}

.brand {
    color: #e50914;
    font-size: 36px;
    font-weight: 900;
    letter-spacing: 2px;
}

.tagline {
    color: #999999;
    font-size: 13px;
    letter-spacing: 0.5px;
}

.hero {
    background: linear-gradient(110deg, #242424, #151515);
    padding: 45px 35px;
    border-radius: 12px;
    margin-top: 25px;
    margin-bottom: 35px;
    border: 1px solid #303030;
}

.hero-label {
    color: #e50914;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 3px;
}

.hero-title {
    color: white;
    font-size: 39px;
    font-weight: 900;
    margin-top: 14px;
    letter-spacing: -1.5px;
}

.hero-desc {
    color: #cccccc;
    font-size: 15px;
    line-height: 1.8;
    max-width: 650px;
}

.section-title {
    color: white;
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-top: 25px;
    margin-bottom: 15px;
}

.stButton > button {
    background-color: #e50914;
    color: white;
    border: none;
    border-radius: 5px;
    font-weight: 700;
    transition: all 0.25s ease;
}

.stButton > button:hover {
    background-color: #b80710;
    color: white;
    border: none;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #191919;
    border: 1px solid #303030;
    border-radius: 9px;
    transition: all 0.25s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border: 1px solid #e50914;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background-color: #252525;
    color: white;
    border: 1px solid #444444;
    border-radius: 5px;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #252525;
}

div[role="radiogroup"] {
    gap: 15px;
}

div[role="radiogroup"] label {
    color: white;
    font-weight: 700;
}

/* CINEMATIC INTRO */

.intro-screen {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    background: #080808;
    z-index: 999999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    animation: introExit 3.2s ease forwards;
}

.intro-logo {
    color: white;
    font-size: 65px;
    font-weight: 900;
    letter-spacing: 5px;
    animation: logoReveal 1.3s ease-out forwards;
    text-shadow: 0 0 25px rgba(229, 9, 20, 0.3);
}

.intro-logo span {
    color: #e50914;
}

.intro-line {
    height: 4px;
    width: 0;
    margin-top: 20px;
    border-radius: 10px;
    background: #e50914;
    box-shadow: 0 0 18px #e50914;
    animation: lineReveal 1.1s ease-out 0.5s forwards;
}

.intro-subtitle {
    color: #888888;
    font-size: 11px;
    letter-spacing: 5px;
    margin-top: 22px;
    opacity: 0;
    animation: subtitleReveal 0.8s ease 0.8s forwards;
}

@keyframes logoReveal {
    0% {
        opacity: 0;
        transform: scale(0.75);
        letter-spacing: 15px;
    }
    100% {
        opacity: 1;
        transform: scale(1);
        letter-spacing: 5px;
    }
}

@keyframes lineReveal {
    from { width: 0; }
    to { width: 190px; }
}

@keyframes subtitleReveal {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes introExit {
    0%, 75% {
        opacity: 1;
        visibility: visible;
    }
    100% {
        opacity: 0;
        visibility: hidden;
        pointer-events: none;
    }
}

.profile-card {
    background: linear-gradient(120deg, #252525, #151515);
    border: 1px solid #393939;
    border-radius: 12px;
    padding: 28px;
}

.profile-avatar {
    width: 85px;
    height: 85px;
    border-radius: 50%;
    background: #e50914;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 35px;
    font-weight: 900;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)


# ---------------- CINEMATIC INTRO ----------------

if not st.session_state.intro_shown:

    st.html("""
    <div class="intro-screen">
        <div class="intro-logo">
            BOOK<span>FLIX</span>
        </div>
        <div class="intro-line"></div>
        <div class="intro-subtitle">
            STORIES BEGIN HERE
        </div>
    </div>
    """)

    st.session_state.intro_shown = True


# ---------------- HEADER ----------------

col1, col2 = st.columns([3, 1])

with col1:

    st.markdown(
        '<div class="brand">BOOKFLIX 📚</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="tagline">Discover stories. Find your next favourite.</div>',
        unsafe_allow_html=True
    )

with col2:

    st.markdown("<br>", unsafe_allow_html=True)

    profile_name = st.session_state.profile.get("name", "")

    if profile_name:
        st.markdown(f"**👋 Welcome, {html.escape(profile_name)}**")
    else:
        st.markdown("**👋 Welcome, Reader**")

    st.markdown(
        f"**📚 {len(st.session_state.reading_list)} SAVED BOOKS**"
    )


st.divider()


# ---------------- NAVIGATION ----------------

page = st.radio(
    "Navigation",
    ["HOME", "MY READING LIST", "MY PROFILE"],
    horizontal=True,
    label_visibility="collapsed",
    key="page"
)

st.divider()


# ---------------- BOOK DETAILS VIEW ----------------

if st.session_state.selected_book is not None:

    selected = books[
        books["book_id"] == st.session_state.selected_book
    ]

    if selected.empty:

        st.session_state.selected_book = None
        st.rerun()

    book = selected.iloc[0]
    book_id = int(book["book_id"])

    st.button(
        "← Back",
        on_click=lambda: setattr(
            st.session_state,
            "selected_book",
            None
        )
    )

    st.divider()

    cover_col, details_col = st.columns([1, 2])

    with cover_col:

        isbn = str(book["isbn"]).strip()
        cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"

        st.image(cover_url, width=280)

    with details_col:

        st.markdown(
            f"<h1>{html.escape(str(book['title']))}</h1>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"### By {html.escape(str(book['author']))}"
        )

        st.markdown(f":red[**{book['genre']}**]")
        st.markdown(f"⭐ **{book['rating']} / 5**")
        st.markdown(f"**Publication Year:** {book['year']}")

        user_average, review_count = get_review_statistics(book_id)

        if review_count > 0:
            st.markdown(
                f"🌟 **BookFlix User Rating:** {user_average} / 5"
            )
            st.caption(f"Based on {review_count} user review(s)")
        else:
            st.caption("No user ratings yet. Be the first to review!")

        st.divider()

        st.markdown("### About this book")
        st.write(book["description"])

        if book_id in st.session_state.reading_list:

            if st.button(
                "✓ Remove from My List",
                key=f"detail_remove_{book_id}"
            ):

                remove_from_reading_list(book_id)
                st.success("Book removed from your reading list.")
                st.rerun()

        else:

            if st.button(
                "＋ Add to My List",
                key=f"detail_add_{book_id}"
            ):

                add_to_reading_list(book_id)
                st.success("Book added to your reading list.")
                st.rerun()


    # ---------------- RATING AND REVIEW FORM ----------------

    st.divider()

    st.markdown(
        '<div class="section-title">Rate & Review This Book</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.profile.get("name", "").strip():
        st.info("Set your display name in My Profile before submitting a review.")
    else:

        st.caption(
            f"Your review will appear under the name "
            f"{st.session_state.profile['name']}."
        )

        with st.form(key=f"review_form_{book_id}"):

            user_rating = st.select_slider(
                "Your rating",
                options=[1, 2, 3, 4, 5],
                value=5,
                format_func=lambda value: "⭐" * value
            )

            review_text = st.text_area(
                "Write your review",
                placeholder="What did you think about this book?",
                max_chars=1000
            )

            submit_review = st.form_submit_button(
                "Submit Review",
                use_container_width=True
            )

            if submit_review:

                if not review_text.strip():

                    st.warning("Please write a review before submitting.")

                else:

                    add_review(
                        book_id,
                        user_rating,
                        review_text
                    )

                    st.success("Your rating and review have been saved!")
                    st.rerun()


    # ---------------- DISPLAY USER REVIEWS ----------------

    st.divider()

    st.markdown(
        '<div class="section-title">Reader Reviews</div>',
        unsafe_allow_html=True
    )

    book_reviews = get_book_reviews(book_id)

    if book_reviews:

        average_rating, total_reviews = get_review_statistics(book_id)

        st.markdown(f"### ⭐ {average_rating} / 5")

        st.caption(
            f"Average reader rating from {total_reviews} review(s)"
        )

        st.divider()

        for review in reversed(book_reviews):

            with st.container(border=True):

                reviewer = html.escape(
                    str(review.get("name", "Reader"))
                )

                st.markdown(f"**{reviewer}**")

                st.markdown(
                    f"**{'⭐' * int(review['rating'])}**"
                )

                st.write(review["review"])

                st.caption(
                    f"Posted on {review.get('date', 'Date unavailable')}"
                )

    else:

        st.info(
            "No reviews yet. Be the first reader to share your opinion!"
        )


    # ---------------- AI RECOMMENDATIONS ----------------

    st.divider()

    st.markdown(
        '<div class="section-title">You May Also Like</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "🧠 Recommendations powered by TF-IDF and Cosine Similarity"
    )

    recommendations = recommend_books(
        book["book_id"],
        books,
        number_of_recommendations=4
    )

    if recommendations.empty:

        st.info("No similar books found.")

    else:

        recommendation_columns = st.columns(4)

        for index, (_, recommended_book) in enumerate(
            recommendations.iterrows()
        ):

            with recommendation_columns[index]:

                rec_id = int(recommended_book["book_id"])
                rec_isbn = str(recommended_book["isbn"]).strip()

                rec_cover_url = (
                    f"https://covers.openlibrary.org/b/isbn/{rec_isbn}-L.jpg"
                )

                with st.container(border=True):

                    st.image(rec_cover_url, width=180)

                    st.markdown(f"**{recommended_book['title']}**")

                    st.caption(
                        f"By {recommended_book['author']}"
                    )

                    st.markdown(
                        f":red[{recommended_book['genre']}]"
                    )

                    st.markdown(
                        f"⭐ {recommended_book['rating']} / 5"
                    )

                    st.markdown(
                        f"🧠 Match: **{recommended_book['similarity_score']:.2f}%**"
                    )

                    if rec_id in st.session_state.reading_list:

                        if st.button(
                            "✓ Saved",
                            key=f"rec_remove_{rec_id}",
                            use_container_width=True
                        ):

                            remove_from_reading_list(rec_id)
                            st.rerun()

                    else:

                        if st.button(
                            "＋ My List",
                            key=f"rec_add_{rec_id}",
                            use_container_width=True
                        ):

                            add_to_reading_list(rec_id)
                            st.rerun()

                    st.button(
                        "View Details",
                        key=f"recommend_{rec_id}",
                        on_click=lambda book_id=rec_id: setattr(
                            st.session_state,
                            "selected_book",
                            book_id
                        ),
                        use_container_width=True
                    )


# ---------------- MY READING LIST PAGE ----------------

elif page == "MY READING LIST":

    st.markdown(
        '<div class="section-title">My Reading List</div>',
        unsafe_allow_html=True
    )

    st.caption("Your personal collection of saved books.")

    saved_books = books[
        books["book_id"].isin(st.session_state.reading_list)
    ]

    if saved_books.empty:

        st.info(
            "Your reading list is empty. Explore books and add your favourites!"
        )

    else:

        st.markdown(
            f"**{len(saved_books)} books in your collection**"
        )

        st.divider()

        list_columns = st.columns(4)

        for index, (_, book) in enumerate(saved_books.iterrows()):

            with list_columns[index % 4]:

                book_id = int(book["book_id"])
                isbn = str(book["isbn"]).strip()

                cover_url = (
                    f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
                )

                with st.container(border=True):

                    st.image(cover_url, width=180)

                    st.markdown(f"**{book['title']}**")
                    st.caption(f"By {book['author']}")
                    st.markdown(f":red[{book['genre']}]")
                    st.markdown(f"⭐ {book['rating']} / 5")

                    st.button(
                        "View Details",
                        key=f"list_details_{book_id}",
                        on_click=lambda selected_id=book_id: setattr(
                            st.session_state,
                            "selected_book",
                            selected_id
                        ),
                        use_container_width=True
                    )

                    if st.button(
                        "✕ Remove",
                        key=f"list_remove_{book_id}",
                        use_container_width=True
                    ):

                        remove_from_reading_list(book_id)
                        st.rerun()


# ---------------- MY PROFILE PAGE ----------------

elif page == "MY PROFILE":

    st.markdown(
        '<div class="section-title">My Profile</div>',
        unsafe_allow_html=True
    )

    current_name = st.session_state.profile.get("name", "")

    st.markdown(
        '<div class="tagline">Your personal BookFlix space.</div>',
        unsafe_allow_html=True
    )

    st.divider()

    with st.container(border=True):

        if current_name:

            initial = html.escape(current_name[0].upper())

            st.markdown(
                f"""
                <div class="profile-avatar">{initial}</div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(f"## {html.escape(current_name)}")
            st.caption("BOOKFLIX READER")

        else:

            st.markdown("## Welcome to BookFlix!")
            st.write("Create your reader profile to personalise your experience.")

        st.divider()

        with st.form("profile_form"):

            new_name = st.text_input(
                "Display name",
                value=current_name,
                placeholder="Enter your name",
                max_chars=40
            )

            save_profile_button = st.form_submit_button(
                "Save Profile",
                use_container_width=True
            )

            if save_profile_button:

                if not new_name.strip():

                    st.warning("Please enter a display name.")

                else:

                    save_profile(new_name)
                    st.success("Your profile has been saved!")
                    st.rerun()


    # ---------------- PROFILE STATISTICS ----------------

    my_reviews = [
        review
        for review in st.session_state.reviews
        if review.get("name", "") == current_name and current_name
    ]

    average_given = 0

    if my_reviews:
        average_given = round(
            sum(int(review["rating"]) for review in my_reviews)
            / len(my_reviews),
            1
        )

    st.markdown(
        '<div class="section-title">Your Reading Activity</div>',
        unsafe_allow_html=True
    )

    stat1, stat2, stat3 = st.columns(3)

    stat1.metric(
        "Saved Books",
        len(st.session_state.reading_list)
    )

    stat2.metric(
        "Reviews Written",
        len(my_reviews)
    )

    stat3.metric(
        "Average Rating Given",
        f"{average_given} / 5"
    )

    # ---------------- MY REVIEWS ----------------

    st.markdown(
        '<div class="section-title">My Reviews</div>',
        unsafe_allow_html=True
    )

    if not current_name:

        st.info("Create your profile to start reviewing books.")

    elif my_reviews:

        for review in reversed(my_reviews):

            matching_book = books[
                books["book_id"] == int(review["book_id"])
            ]

            if matching_book.empty:
                continue

            reviewed_book = matching_book.iloc[0]

            with st.container(border=True):

                st.markdown(f"**{reviewed_book['title']}**")

                st.markdown(
                    f"⭐ {int(review['rating'])} / 5"
                )

                st.write(review["review"])

                st.caption(
                    f"Posted on {review.get('date', 'Date unavailable')}"
                )

    else:

        st.info(
            "You haven't written any reviews yet. Explore a book and share your thoughts!"
        )


# ---------------- HOME PAGE ----------------

else:

    featured = books.iloc[0]

    featured_col1, featured_col2 = st.columns([1, 2])

    with featured_col1:

        featured_isbn = str(featured["isbn"]).strip()

        featured_cover = (
            f"https://covers.openlibrary.org/b/isbn/{featured_isbn}-L.jpg"
        )

        st.image(featured_cover, width=250)

    with featured_col2:

        st.html(f"""
        <div class="hero">
            <div class="hero-label">FEATURED BOOK</div>

            <div class="hero-title">
                {html.escape(str(featured['title']))}
            </div>

            <div class="hero-desc">
                {html.escape(str(featured['description']))}
            </div>

            <br>

            <div style="color:#aaaaaa;">
                Author: {html.escape(str(featured['author']))}
                &nbsp; | &nbsp;
                ⭐ {featured['rating']}
                &nbsp; | &nbsp;
                {featured['year']}
            </div>
        </div>
        """)

        featured_id = int(featured["book_id"])

        if featured_id in st.session_state.reading_list:

            if st.button(
                "✓ Remove Featured Book from My List",
                key="featured_remove"
            ):

                remove_from_reading_list(featured_id)
                st.rerun()

        else:

            if st.button(
                "＋ Add Featured Book to My List",
                key="featured_add"
            ):

                add_to_reading_list(featured_id)
                st.rerun()


    # ---------------- SEARCH AND FILTER ----------------

    st.markdown(
        '<div class="section-title">Explore Books</div>',
        unsafe_allow_html=True
    )

    search_col, genre_col = st.columns([2, 1])

    with search_col:

        search = st.text_input(
            "Search",
            placeholder="Search by book title or author..."
        )

    with genre_col:

        genres = ["All Genres"] + sorted(
            books["genre"].unique().tolist()
        )

        selected_genre = st.selectbox(
            "Choose Genre",
            genres
        )


    # ---------------- FILTER BOOKS ----------------

    filtered_books = books.copy()

    if search:

        filtered_books = filtered_books[
            filtered_books["title"].str.contains(
                search,
                case=False,
                na=False
            ) |
            filtered_books["author"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    if selected_genre != "All Genres":

        filtered_books = filtered_books[
            filtered_books["genre"] == selected_genre
        ]


    st.markdown(
        f'<div class="tagline">{len(filtered_books)} books found</div>',
        unsafe_allow_html=True
    )


    # ---------------- DISPLAY BOOK CARDS ----------------

    if filtered_books.empty:

        st.warning("No books found. Try another search.")

    else:

        book_columns = st.columns(4)

        for index, (_, book) in enumerate(filtered_books.iterrows()):

            with book_columns[index % 4]:

                book_id = int(book["book_id"])
                isbn = str(book["isbn"]).strip()

                cover_url = (
                    f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
                )

                with st.container(border=True):

                    st.image(cover_url, width=180)

                    st.markdown(f"**{book['title']}**")
                    st.caption(f"By {book['author']}")
                    st.markdown(f":red[{book['genre']}]")
                    st.markdown(f"⭐ {book['rating']} / 5")

                    average_rating, review_count = get_review_statistics(book_id)

                    if review_count > 0:
                        st.caption(
                            f"🌟 Reader rating: {average_rating}/5 ({review_count})"
                        )

                    if book_id in st.session_state.reading_list:

                        if st.button(
                            "✓ Saved to My List",
                            key=f"home_remove_{book_id}",
                            use_container_width=True
                        ):

                            remove_from_reading_list(book_id)
                            st.rerun()

                    else:

                        if st.button(
                            "＋ Add to My List",
                            key=f"home_add_{book_id}",
                            use_container_width=True
                        ):

                            add_to_reading_list(book_id)
                            st.rerun()

                    st.button(
                        "View Details",
                        key=f"details_{book_id}",
                        on_click=lambda selected_id=book_id: setattr(
                            st.session_state,
                            "selected_book",
                            selected_id
                        ),
                        use_container_width=True
                    )


# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    "<center style='color:#777777;'>"
    "BOOKFLIX | Your next favourite story awaits."
    "</center>",
    unsafe_allow_html=True
)
