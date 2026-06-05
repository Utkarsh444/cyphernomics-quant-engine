class ElliottValidator:

    @staticmethod
    def validate(
        wave_count
    ):

        if wave_count is None:
            return False

        return (
            wave_count
            >= 5
        )
