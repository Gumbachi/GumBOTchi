from typing import List
import database as db
import requests
from .time_series import DataType, TimeInterval, TimeSeriesData


class AlphaVantageError(Exception):
    pass


class AlphaVantage:
    def __init__(self, guild_id: int) -> None:
        self.API_KEY = db.get_alphavantage(id=guild_id)

        if self.API_KEY is None:
            raise AlphaVantageError("Missing API KEY")

    def get_url(
        self,
        ticker: str,
        data_type: DataType,
        interval: TimeInterval = TimeInterval.FIVE,
    ):
        """
        Gets the method for retrieving specified data type.

        Parameters:
        data_type: DataType - Type of data requested

        Returns:
        classmethod - method used to retrieve specified data type
        """
        match data_type:
            case DataType.INTRADAY:
                return f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval={interval.value}&outputsize=full&apikey={self.API_KEY}"
            case DataType.DAILY:
                return f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&outputsize=full&apikey={self.API_KEY}"
            case DataType.WEEKLY:
                return f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={ticker}&outputsize=full&apikey={self.API_KEY}"
            case DataType.MONTHLY:
                return f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={ticker}&outputsize=full&apikey={self.API_KEY}"

        return None

    def get_data(self, url: str, data_type: DataType) -> List[TimeSeriesData]:
        """
        Gets data according to url. Uses 1 API Request.

        Returns:
        List[TimeSeriesData]
        """
        try:
            request = requests.get(url)
            data = request.json()

            if data.get("Note"):
                return print("Out of API calls, try again later.")

            data = TimeSeriesData.load_json(data_type=data_type, data=data)
            return data
        except Exception as e:
            raise AlphaVantageError(f"Error getting data: {e}")
