from auth import login_user, register_user
from database import get_profile, init_db
from profile_manager import (
    create_or_update_profile,
    show_profile,
)
from recommender import SchemeSetuEngine


def recommendation_menu(user):
    profile = get_profile(user["id"])

    if not profile:
        print(
            "\nBefore searching schemes, "
            "create your eligibility profile."
        )
        profile = create_or_update_profile(user)

    try:
        engine = SchemeSetuEngine()
    except FileNotFoundError as exc:
        print("\n", exc)
        return

    query = input(
        "\nDescribe the type of assistance you need\n"
        "(example: scholarship for engineering student):\n> "
    ).strip()

    if not query:
        print("Search query cannot be empty.")
        return

    results = engine.recommend(
        user_query=query,
        profile=profile,
        top_k=10,
    )

    if results.empty:
        print("No recommendations found.")
        return

    print("\n" + "=" * 75)
    print("                   TOP SCHEME RECOMMENDATIONS")
    print("=" * 75)
    print(
        "Important: Match score is recommendation relevance, "
        "not a legal guarantee of eligibility."
    )

    for number, (_, row) in enumerate(
        results.iterrows(),
        start=1,
    ):
        print("\n" + "-" * 75)
        print(
            f"{number}. {row.get('name', 'Unnamed Scheme')}"
        )
        print(
            f"Recommendation Match: "
            f"{row.get('match_score', 0):.2f}%"
        )

        if row.get("level"):
            print("Level:", row.get("level"))

        if row.get("schemeCategory"):
            print(
                "Category:",
                str(row.get("schemeCategory"))[:250],
            )

        if row.get("eligibility"):
            print("\nEligibility:")
            print(str(row.get("eligibility"))[:1200])

        if row.get("benefits"):
            print("\nBenefits:")
            print(str(row.get("benefits"))[:900])

        if row.get("documents"):
            print("\nDocuments:")
            print(str(row.get("documents"))[:700])

        if row.get("application"):
            print("\nApplication:")
            print(str(row.get("application"))[:700])


def user_dashboard(user):
    while True:
        print("\n" + "=" * 60)
        print(f"        SCHEMESETU - WELCOME {user['name'].upper()}")
        print("=" * 60)
        print("1. Find schemes")
        print("2. Create / Update eligibility profile")
        print("3. View my profile")
        print("4. Logout")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            recommendation_menu(user)

        elif choice == "2":
            create_or_update_profile(user)

        elif choice == "3":
            show_profile(user)

        elif choice == "4":
            print("\nLogged out successfully.")
            break

        else:
            print("Invalid choice. Enter 1-4.")


def main():
    init_db()

    while True:
        print("\n" + "=" * 60)
        print("                       SCHEMESETU")
        print("          Government Scheme Recommendation System")
        print("=" * 60)
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            user = login_user()

            if user:
                user_dashboard(user)

        elif choice == "2":
            register_user()

        elif choice == "3":
            print("\nThank you for using SchemeSetu.")
            break

        else:
            print("Invalid choice. Enter 1, 2 or 3.")


if __name__ == "__main__":
    main()
