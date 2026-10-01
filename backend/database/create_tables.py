from app.core.database import Base, engine
from app.models import SurveyProject


def main():
    Base.metadata.create_all(bind=engine)
    print("ELIOS-LAND database tables created successfully.")


if __name__ == "__main__":
    main()
