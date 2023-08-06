import logging
from configparser import ConfigParser

from langchain.chat_models import ChatOpenAI
from llama_index import GPTVectorStoreIndex, LLMPredictor, ServiceContext
from llama_index.readers.database import DatabaseReader

logging.basicConfig(filename="llama_index.log", filemode='a', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class GPTLLamaIndexClass:
    def __init__(self, context):
        self.__initVal()
        self.__init(context)

    def __initVal(self):
        config = ConfigParser()
        config.read("config.ini")
        self.general_schema = 'general'
        self.__model = config.get("General", "model")
        self.__temperature = config.getfloat("General", "temperature")
        self.__streaming = config.getboolean("General", "stream")
        self.__chunk_size = config.getint("General", "chunk_size")
        self.__similarity_top_k = config.getint("General", "similarity_top_k")
        self.__db = DatabaseReader(
            scheme=config.get("DB", "SCHEME"),  # Database Scheme
            host=config.get("DB", "HOST"),  # Database Host
            port=config.get("DB", "PORT"),  # Database Port
            user=config.get("DB", "USER"),  # Database User
            password=config.get("DB", "PASSWORD"),  # Database Password
            dbname=config.get("DB", "DBNAME"),  # Database Name
        )

    def __init(self, context):
        context_table_name_list = [table_name.text for table_name in self.__db.load_data(query=f"""SELECT table_name
        FROM information_schema.tables WHERE table_schema = '{context.lower()}' AND table_type = 'BASE TABLE';""")]

        general_table_name_list = [table_name.text for table_name in self.__db.load_data(query=f"""SELECT table_name
        FROM information_schema.tables WHERE table_schema = '{self.general_schema}' AND table_type = 'BASE TABLE';""")]

        documents = []
        for table_name in context_table_name_list:
            query = f"SELECT CONCAT('query: ',query ,' answer: ',answer) FROM {context}.{table_name}"
            documents.extend(self.__db.load_data(query=query))
        for table_name in general_table_name_list:
            query = f"SELECT CONCAT('query: ',query ,' answer: ',answer) FROM {self.general_schema}.{table_name}"
            documents.extend(self.__db.load_data(query=query))

        llm_predictor = LLMPredictor(
            llm=ChatOpenAI(temperature=self.__temperature, model_name=self.__model, streaming=self.__streaming))
        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, chunk_size=self.__chunk_size)
        index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)

        self.__query_engine = index.as_query_engine(service_context=service_context,
                                                    similarity_top_k=self.__similarity_top_k, streaming=True)

    def getResponse(self, text):
        return self.__query_engine.query(text)
