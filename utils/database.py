from datetime import datetime

from utils.supabase_client import get_supabase_client


# ---------------- PROFILE DATABASE ----------------

def get_profile(user_id):
    """Fetch a reader's profile."""
    supabase = get_supabase_client()

    response = (
        supabase.table("profiles")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )

    return response.data


def save_profile(user_id, display_name):
    """Create or update a reader's profile."""
    supabase = get_supabase_client()

    response = (
        supabase.table("profiles")
        .upsert({
            "id": user_id,
            "display_name": display_name.strip()
        })
        .execute()
    )

    return response.data


# ---------------- READING LIST DATABASE ----------------

def get_reading_list(user_id):
    """Fetch the logged-in reader's saved book IDs."""
    supabase = get_supabase_client()

    response = (
        supabase.table("reading_lists")
        .select("book_id")
        .eq("user_id", user_id)
        .execute()
    )

    return [
        int(item["book_id"])
        for item in response.data
    ]


def add_reading_list_book(user_id, book_id):
    """Save a book to the reader's list."""
    supabase = get_supabase_client()

    response = (
        supabase.table("reading_lists")
        .upsert(
            {
                "user_id": user_id,
                "book_id": int(book_id)
            },
            on_conflict="user_id,book_id"
        )
        .execute()
    )

    return response.data


def remove_reading_list_book(user_id, book_id):
    """Remove a book from the reader's list."""
    supabase = get_supabase_client()

    response = (
        supabase.table("reading_lists")
        .delete()
        .eq("user_id", user_id)
        .eq("book_id", int(book_id))
        .execute()
    )

    return response.data


# ---------------- REVIEWS DATABASE ----------------

def get_reviews():
    """Fetch reviews visible under the reviews table's RLS policies."""
    supabase = get_supabase_client()

    response = (
        supabase.table("reviews")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def add_review(user_id, book_id, reviewer_name, rating, review_text):
    """Insert a review belonging to the currently signed-in reader."""
    supabase = get_supabase_client()

    response = (
        supabase.table("reviews")
        .insert({
            "user_id": user_id,
            "book_id": int(book_id),
            "reviewer_name": reviewer_name.strip() or "Reader",
            "rating": int(rating),
            "review_text": review_text.strip(),
        })
        .execute()
    )

    return response.data
