from typing import Optional

class Response:
    def __init__(
        self,
        text: str,
        chat_id: Optional[str] = None,
        deepthink_duration: Optional[int] = None,
        deepthink_content: Optional[str] = None,
        search_results: Optional[list] = None
    ):
        """Response object to store the response from the DeepSeek API.

        Args:
        ----------
            text (str): The response text.
            chat_id (Optional[str], optional): The chat ID. Defaults to None.
            deepthink_duration (Optional[int], optional): The deepthink duration. Defaults to None.
            deepthink_content (Optional[str], optional): The deepthink content. Defaults to None.
            search_results (Optional[list], optional): The search results. Defaults to None.
        """
        self.text = text
        self.chat_id = chat_id
        self.deepthink_duration = deepthink_duration
        self.deepthink_content = deepthink_content
        self.search_results = search_results
    
    def __repr__(self):
        return self.text

class SearchResult:
    def __init__(
        self,
        image_url: str,
        website: str,
        date: str,
        index: int,
        title: str,
        description: str
    ):
        """Search result object to store the search result data.

        Args:
        ----------
            image_url (str): The image URL.
            website (str): The website name.
            date (str): The date of publish.
            index (int): The index of the result. (starts from 1)
            title (str): The title of the result.
            description (str): The description of the result.
        """
        self.image_url = image_url
        self.website = website
        self.date = date
        self.index = index
        self.title = title
        self.description = description
    
    def __repr__(self):
        return f"SearchResult(\n\timage_url = {self.image_url},\n\twebsite = {self.website},\n\tdate = {self.date},\n\tindex = {self.index},\n\ttitle = {self.title},\n\tdescription = {self.description}\n)"
