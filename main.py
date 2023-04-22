import os
import tweepy
import time
import locale

from safeScheduler import SafeScheduler
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv


TORCEDOMETRO_FILE = "torcedometro_value.txt"

def publish_on_twitter(current_value, difference):
  # Authenticate to Twitter
  
  auth = tweepy.Client(consumer_key=os.getenv('TWITTER_API_KEY'),
                       consumer_secret=os.getenv('TWITTER_API_SECRET'),
                       access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                       access_token_secret=os.getenv('TWITTER_ACCESS_SECRET'))

  locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
  formatted_current_value = locale.format_string("%.0f", current_value, grouping=True)
  formatted_difference = locale.format_string("%.0f", difference, grouping=True)
  
  if difference >= 0:
    emoji = "🔺"
  else:
    emoji = "🔻"
  
  status_to_publish = f"""
📈🦁 Atualização Sou Mais Vitória! 

👥 Sócios atuais: {formatted_current_value}
{emoji} Diferença: {"+" if difference > 0 else ""}{formatted_difference} desde a última atualização

👉 Torne-se Sócio Sou Mais Vitória e ajude o Vitória: 
https://socio-vitoria.futebolcard.com/
  
  """
  #api.update_status(status=status_to_publish)
  # Replace the text with whatever you want to Tweet about
  response = auth.create_tweet(text=status_to_publish)
  print(response)

def scrap_torcedometro_tag():
    # Define the elements to be used in the function
    torcedometro_element = None
    torcedometro_text = None
    torcedometro_value = None

    # Open the website using Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    with webdriver.Chrome(options=options) as driver:
        driver.get("https://socio-vitoria.futebolcard.com/")

        # Find the "torcedometro" element by ID
        torcedometro_element = driver.find_element(By.ID, "torcedometro")
        print("Found Torcedometro TAG")

        # Concatenate the text of all child "span" elements into a string
        print("Converting Spans to Integer")
        torcedometro_text = "".join([span.text for span in torcedometro_element.find_elements(By.TAG_NAME, "span")])

        # Convert the string to an integer
        torcedometro_value = int(torcedometro_text)

    # Read the previous value from the file, or create the file if it doesn't exist
    try:
        with open(TORCEDOMETRO_FILE, "r") as f:
            previous_value = int(f.read().strip())
    except FileNotFoundError:
        previous_value = torcedometro_value

    # Calculate the difference between the new value and the previous value
    difference = torcedometro_value - previous_value

    # Print the result
    print(f"New value: {torcedometro_value}")
    print(f"Difference: {difference}")
    #if difference != 0:
    #    publish_on_twitter(torcedometro_value, difference=difference)

    publish_on_twitter(torcedometro_value, difference=difference)
    # Write the new value to the file
    with open(TORCEDOMETRO_FILE, "w") as f:
        f.write(str(torcedometro_value))

    # Return the torcedometro value
    return torcedometro_value


# Schedule the script to run after a 10-minute delay
load_dotenv()
scheduler = SafeScheduler()
scheduler.every(30).minutes.do(scrap_torcedometro_tag)

scrap_torcedometro_tag()
while True:
    scheduler.run_pending()
    time.sleep(1)