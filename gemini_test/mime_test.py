import mimetypes
file_path = "test.pdf"
mime_type, _ = mimetypes.guess_type(file_path)
print(type(mime_type))
print(f"The MIME type of the file is: {mime_type}")

file_path = "sound.mp3"
mime_type, _ = mimetypes.guess_type(file_path)
print(f"The MIME type of the file is: {mime_type}")

file_path = "image.jpg"
mime_type, _ = mimetypes.guess_type(file_path)
print(f"The MIME type of the file is: {mime_type}")