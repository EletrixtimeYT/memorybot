import discord
import os
import asyncio
import yaml

def mask_token(token):
    if len(token) > 3:
        masked_chars = '*' * (len(token) - 3)
        masked_token = token[:3] + masked_chars
        return masked_token
    else:
        return token

with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

token = config.get("token")
target_categoryid = int(config.get("target_category_id"))
destination_channel = int(config.get("destination_channel_id"))
target_filename = config.get("target_filename")
statuttext = config.get("textstatut")
delay = int(config.get("delay"))

# Ouvrir le fichier logs.txt en mode append (ajout)
logs_file = open("crashreport.txt", "a")

def log_to_file(log_message):
    logs_file.write(log_message + "\n")
    logs_file.flush()  # Forcer l'écriture immédiate dans le fichier

print("EletrixUtils", file=logs_file)

print("=================", file=logs_file)
print("Categorie ID : ", file=logs_file)
print(target_categoryid, file=logs_file)
print("=================", file=logs_file)
print("Channel Destination : ", file=logs_file)
print(destination_channel, file=logs_file)
print("=================", file=logs_file)
print("Target filename : ", file=logs_file)
print(target_filename, file=logs_file)
print("=================", file=logs_file)
print("Statut text : ", file=logs_file)
print(statuttext, file=logs_file)
print("=================", file=logs_file)
print("Delay : ", file=logs_file)
print(delay, file=logs_file)
print("=================", file=logs_file)
print("Token : ", file=logs_file)
print(mask_token(token), file=logs_file)
print("=================", file=logs_file)

intents = discord.Intents.default()

client = discord.Client(intents=intents)

async def process_category():
    # Récupérer la catégorie cible par son ID
    target_category = client.get_channel(target_categoryid)
    if target_category is None:
        print("Catégorie introuvable.")
        return

       # Parcourir tous les canaux de la catégorie
    for channel in target_category.channels:
        if isinstance(channel, discord.TextChannel) and channel.id != destination_channel:
            await process_channel(channel, destination_channel, target_filename)

    # Attendre 1 minute avant de relancer le traitement
    await asyncio.sleep(delay)
    await process_category()

async def process_channel(channel, destination_channel, target_filename):
    async for message in channel.history(limit=None):
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename == target_filename:
                    # Sauvegarder le fichier localement
                    await attachment.save(attachment.filename)

                    # Réenvoyer le fichier sauvegardé sur le canal de destination
                    destination_channel = client.get_channel(destination_channel)
                    await destination_channel.send(file=discord.File(attachment.filename))

                    # Supprimer le message d'origine
                    await message.delete()

                    # Supprimer le fichier sauvegardé localement
                    os.remove(attachment.filename)

@client.event
async def on_ready():
        # Charger les informations de configuration depuis le fichier "config.yml"

    activity = discord.Game(name=statuttext, type=3)
    await client.change_presence(status=discord.Status.idle, activity=activity)
    # Lancer le processus de vérification de la catégorie toutes les 1 minute
    await process_category()


try:
    client.run(token)
except Exception as e:
    print("The Bot just crashed please report this crash to creator !")
    print(f"Error: {e}", file=logs_file)
finally:
    logs_file.close()