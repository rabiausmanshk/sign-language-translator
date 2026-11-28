
from remotezip import RemoteZip

URL = (
    "https://download.microsoft.com/download/b/8/8/"
    "b88c0bae-e6c1-43e1-8726-98cf5af36ca4/"
    "ASL_Citizen.zip"
)

print("Connecting to ASL Citizen archive...")

try:
    with RemoteZip(URL) as archive:
        print("\nRemote archive connected!")

        files = archive.namelist()

        print("\nTotal entries:", len(files))

        print("\nCSV files:")
        for filename in files:
            if filename.lower().endswith(".csv"):
                print(filename)

        print("\nPotential video directories:")
        for filename in files:
            if filename.lower().endswith(".mp4"):
                print(filename)
                break

except Exception as error:
    print("\nRemote inspection failed.")
    print("Error:", error)
    print(
        "The server may not support the required "
        "HTTP range requests, or the connection may "
        "have failed."
    )
