import os
import asyncio
from dotenv import load_dotenv
import sys

# Add Azure OpenAI package
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, EnvironmentCredential
from azure.monitor.opentelemetry import configure_azure_monitor

# Set to True to print the full response from OpenAI for each call
printFullResponse = False

os.environ['AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED'] = 'true'

async def main():    
    try: 
    
        # Get configuration settings 
        load_dotenv()
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
        azure_oai_model = os.getenv("AZURE_OAI_MODEL")
        azure_oai_api_version = os.getenv("AZURE_OAI_API_VERSION")
        # Configure the Azure OpenAI client
        # client = AzureOpenAI(
        #     azure_endpoint = azure_oai_endpoint, 
        #     api_key=azure_oai_key,  
        #     api_version=azure_oai_api_version
        # )
        project_connection_string = os.environ["PROJECT_CONNECTION_STRING"]

        with AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=project_connection_string,
        ) as project_client:
            
            application_insights_connection_string = project_client.telemetry.get_connection_string()
            configure_azure_monitor(connection_string=application_insights_connection_string)

            # Enable console tracing
            # or, if you have local OTLP endpoint running, change it to
            # project_client.telemetry.enable(destination="http://localhost:4317")
            # project_client.telemetry.enable(destination=sys.stdout)

            # Get an authenticated OpenAI client for your default Azure OpenAI connection:
            with project_client.inference.get_azure_openai_client(api_version=azure_oai_api_version) as client:
                while True:
                    # Pause the app to allow the user to enter the system prompt
                    print("------------------\nPausing the app to allow you to change the system prompt.\nPress enter to continue...")
                    input()

                    # Read in system message and prompt for user message
                    system_text = open(file="system.txt", encoding="utf8").read().strip()
                    user_text = input("Enter user message, or 'quit' to exit: ")
                    if user_text.lower() == 'quit' or system_text.lower() == 'quit':
                        print('Exiting program...')
                        break
                    
                    await call_openai_model(
                        client,
                        system_message = system_text, 
                        user_message = user_text, 
                        model=azure_oai_deployment
                    )

    except Exception as ex:
        print(ex)

async def loop_call_openai_aiproject():


async def call_openai_model(client, system_message, user_message, model):
    # Format and send the request to the model
    messages =[
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    # Call the Azure OpenAI model
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=800
    )


    if printFullResponse:
        print(response)

    print("Response:\n" + response.choices[0].message.content + "\n")

if __name__ == '__main__': 
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    asyncio.run(main())
