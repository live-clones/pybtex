from pybtex.database import BibliographyData, Entry, Person

reference_data = BibliographyData(
    entries=[
        (
            "viktorov-metodoj",
            Entry(
                "book",
                fields=[
                    ("publisher", "Л.: <<Химия>>"),
                    ("language", "russian"),
                    ("year", "1977"),
                    (
                        "title",
                        "Методы вычисления физико-химических величин и прикладные расчёты",
                    ),
                ],
                persons={"author": [Person("Викторов, Михаил Маркович")]},
            ),
        ),
        (
            "test-booklet",
            Entry(
                "booklet",
                fields=[
                    ("year", "2006"),
                    ("month", "January"),
                    ("title", "Just a booklet"),
                    ("howpublished", "Published by Foo"),
                    ("language", "english"),
                    ("address", "Moscow"),
                ],
                persons={"author": [Person("de Last, Jr., First Middle")]},
            ),
        ),
        (
            "ruckenstein-diffusion",
            Entry(
                "article",
                fields=[
                    ("language", "english"),
                    (
                        "title",
                        "Predicting the Diffusion Coefficient in Supercritical Fluids",
                    ),
                    ("journal", "Ind. Eng. Chem. Res."),
                    ("volume", "36"),
                    ("year", "1997"),
                    ("pages", "888-895"),
                ],
                persons={
                    "author": [Person("Liu, Hongquin"), Person("Ruckenstein, Eli")]
                },
            ),
        ),
        (
            "test-inbook",
            Entry(
                "inbook",
                fields=[
                    ("title", "Some Title"),
                    ("booktitle", "Some Good Book"),
                    ("series", "Some series"),
                    ("number", "3"),
                    ("publisher", "Some Publisher"),
                    ("edition", "Second"),
                    ("language", "english"),
                    ("year", "1933"),
                    ("pages", "44--59"),
                ],
                persons={"author": [Person("Jackson, Peter")]},
            ),
        ),
    ],
    preamble=["%%% pybtex example file"],
)
