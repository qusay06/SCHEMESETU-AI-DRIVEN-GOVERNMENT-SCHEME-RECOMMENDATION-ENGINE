from database import get_profile, save_profile


def ask_choice(prompt, choices, allow_skip=False):
    while True:
        print(f"\n{prompt}")

        for index, choice in enumerate(choices, start=1):
            print(f"{index}. {choice}")

        if allow_skip:
            print("0. Prefer not to say / Skip")

        value = input("> ").strip()

        if allow_skip and value == "0":
            return ""

        if value.isdigit():
            index = int(value)

            if 1 <= index <= len(choices):
                return choices[index - 1]

        print("Invalid choice. Please try again.")


def ask_yes_no(prompt, allow_skip=False):
    options = ["Yes", "No"]
    return ask_choice(prompt, options, allow_skip=allow_skip)


def ask_int(prompt, minimum=None, maximum=None, allow_skip=False):
    while True:
        value = input(f"{prompt}: ").strip()

        if allow_skip and value == "":
            return None

        try:
            number = int(value)

            if minimum is not None and number < minimum:
                raise ValueError

            if maximum is not None and number > maximum:
                raise ValueError

            return number

        except ValueError:
            extra = ""
            if minimum is not None and maximum is not None:
                extra = f" ({minimum}-{maximum})"
            print(f"Enter a valid whole number{extra}.")


def ask_float(prompt, minimum=0, allow_skip=False):
    while True:
        value = input(f"{prompt}: ").strip().replace(",", "")

        if allow_skip and value == "":
            return None

        try:
            number = float(value)

            if number < minimum:
                raise ValueError

            return number

        except ValueError:
            print("Enter a valid number.")


def create_or_update_profile(user):
    print("\n" + "=" * 60)
    print("                 ELIGIBILITY PROFILE")
    print("=" * 60)
    print("These details are used only for scheme matching.")
    print("Sensitive optional questions may be skipped.\n")

    profile = {}

    profile["applicant_type"] = ask_choice(
        "Who are you applying as?",
        [
            "Individual",
            "Student",
            "Farmer",
            "Worker",
            "Entrepreneur / Business Owner",
            "Institution / Organization",
        ],
    )

    profile["age"] = ask_int(
        "Age",
        minimum=0,
        maximum=120,
    )

    profile["gender"] = ask_choice(
        "Gender",
        [
            "Male",
            "Female",
            "Transgender",
            "Other",
        ],
        allow_skip=True,
    )

    profile["state"] = input(
        "\nState / Union Territory: "
    ).strip()

    profile["district"] = input(
        "District: "
    ).strip()

    profile["area_type"] = ask_choice(
        "Area type",
        ["Rural", "Urban"],
        allow_skip=True,
    )

    profile["annual_income"] = ask_float(
        "\nAnnual family income in INR",
        minimum=0,
    )

    profile["social_category"] = ask_choice(
        "Social category",
        ["General", "OBC", "SC", "ST", "EWS"],
        allow_skip=True,
    )

    profile["occupation"] = ask_choice(
        "Current occupation/status",
        [
            "Student",
            "Employed",
            "Unemployed",
            "Farmer",
            "Agricultural Labourer",
            "Construction / Other Worker",
            "Self-employed",
            "Entrepreneur",
            "Senior Citizen",
            "Homemaker",
            "Institution / Organization",
            "Other",
        ],
    )

   # Ask BPL status only when annual income is not ₹2,00,000
    if profile["annual_income"] == 200000:
     profile["bpl_status"] = ""
    else:
     profile["bpl_status"] = ask_yes_no(
        "Does your family belong to BPL (Below Poverty Line)?",
        allow_skip=True,
    )

    profile["marital_status"] = ask_choice(
        "Marital status",
        [
            "Single",
            "Married",
            "Widowed",
            "Divorced",
            "Separated",
        ],
        allow_skip=True,
    )

    profile["minority_status"] = ask_yes_no(
        "Do you want to identify as belonging to a notified minority community?",
        allow_skip=True,
    )

    # Student-specific criteria
    is_student = (
        profile["applicant_type"] == "Student"
        or profile["occupation"] == "Student"
    )

    profile["is_student"] = "Yes" if is_student else "No"

    if is_student:
        profile["education_level"] = ask_choice(
            "Current education level",
            [
                "School",
                "ITI",
                "Diploma",
                "Undergraduate",
                "Postgraduate",
                "PhD",
                "Other",
            ],
        )

        profile["course"] = input(
            "\nCourse / programme: "
        ).strip()

        profile["study_year"] = input(
            "Current class / year of study: "
        ).strip()

        profile["institution_type"] = ask_choice(
            "Institution type",
            [
                "Government",
                "Government Aided",
                "Private",
                "Other",
            ],
            allow_skip=True,
        )

    # Disability criteria
    profile["has_disability"] = ask_yes_no(
        "Do you have a disability?",
        allow_skip=True,
    )

    if profile["has_disability"] == "Yes":
        profile["disability_percentage"] = ask_float(
            "Disability percentage",
            minimum=0,
        )

    # Farmer-specific criteria
    is_farmer = (
        profile["applicant_type"] == "Farmer"
        or profile["occupation"] in [
            "Farmer",
            "Agricultural Labourer",
        ]
    )

    profile["is_farmer"] = "Yes" if is_farmer else "No"

    if is_farmer:
        profile["land_ownership"] = ask_yes_no(
            "Do you own agricultural land?",
            allow_skip=True,
        )

        profile["land_size_acres"] = ask_float(
            "Landholding size in acres (press Enter to skip)",
            minimum=0,
            allow_skip=True,
        )

        profile["farmer_type"] = ask_choice(
            "Farmer type",
            [
                "Marginal Farmer",
                "Small Farmer",
                "Medium Farmer",
                "Large Farmer",
                "Tenant Farmer",
                "Agricultural Labourer",
            ],
            allow_skip=True,
        )

    # Business-specific criteria
    if profile["applicant_type"] == "Entrepreneur / Business Owner" or profile["occupation"] in [
        "Self-employed",
        "Entrepreneur",
    ]:
        profile["business_type"] = ask_choice(
            "Business / enterprise type",
            [
                "Micro",
                "Small",
                "Medium",
                "Startup",
                "Self Help Group",
                "Other",
            ],
            allow_skip=True,
        )

    save_profile(user["id"], profile)

    print("\nEligibility profile saved successfully.")
    return profile


def show_profile(user):
    profile = get_profile(user["id"])

    if not profile:
        print("\nNo eligibility profile found.")
        return

    print("\n" + "=" * 60)
    print("                    YOUR PROFILE")
    print("=" * 60)

    hidden = {"user_id", "updated_at"}

    for key, value in profile.items():
        if key in hidden:
            continue

        if value in (None, ""):
            continue

        label = key.replace("_", " ").title()
        print(f"{label:25}: {value}")
