import os
import re
from fastapi import HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError
import comtypes.client
import sys
import pandas as pd  

from app.schemas import ImageProcessionOptions


def process_file(file_location: str, options: ImageProcessionOptions):
    """Універсальна функция обробки файлів (Зображення, Word, Excel, CSV)"""
    base_path, ext = os.path.splitext(file_location.lower())

    if ext in [".jpg", ".jpeg", ".png", ".webp"]:
        try:
            with Image.open(file_location) as img:
                if options.resize:
                    match = re.match(r"(\d+)x(\d+)", options.resize)
                    if match:
                        width, height = map(int, match.groups())
                        img = img.resize((width, height))

                if options.grayscale:
                    img = ImageOps.grayscale(img)

                if options.flip:
                    if options.flip == "horizontal":
                        img = ImageOps.mirror(img)
                    if options.flip == "vertical":
                        img = ImageOps.flip(img)

                if options.convert_to:
                    save_format = options.convert_to.upper()
                    if save_format == "JPG":
                        save_format = "JPEG"

                    file_location = f"{base_path}.{options.convert_to.lower()}"
                    img.save(file_location, save_format)
                else:
                    img.save(file_location)

            return file_location

        except UnidentifiedImageError:
            raise HTTPException(
                status_code=400,
                detail="Файл пошкоджено або він не є валідним зображенням.",
            )

    # --- 2. ЯКЩО ЦЕ ДОКУМЕНТ WORD ---
    elif ext in ['.docx', '.doc']:
        if options.resize or options.grayscale or options.flip:
            raise HTTPException(
                status_code=400, 
                detail="Графічні опції (resize/grayscale/flip) не можна застосувати до документів Word."
            )

        if options.convert_to and options.convert_to.lower() == 'pdf':
            pdf_location = f"{base_path}.pdf"
            abs_file = os.path.abspath(file_location)
            abs_pdf = os.path.abspath(pdf_location)
            
            comtypes.CoInitialize()
            try:
                word = comtypes.client.CreateObject('Word.Application')
                word.Visible = False 
                
                doc = word.Documents.Open(abs_file)
                doc.SaveAs(abs_pdf, FileFormat=17)
                
                doc.Close()
                word.Quit()
                return pdf_location
                
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Помилка COM-інтерфейсу Windows при конвертації у PDF. Лог: {str(e)}"
                )
            finally:
                comtypes.CoUninitialize()
        
        return file_location

    elif ext in ['.csv', '.xlsx']:
        if options.resize or options.grayscale or options.flip:
            raise HTTPException(
                status_code=400,
                detail="Графічні опції (resize/grayscale/flip) не можна застосувати до таблиць."
            )

        if options.convert_to:
            target_ext = options.convert_to.lower()
            
            if f".{target_ext}" == ext:
                return file_location

            try:
                if ext == '.csv':
                    df = pd.read_csv(file_location)
                else:
                    df = pd.read_excel(file_location)

                # Записуємо у новий формат
                if target_ext == 'csv':
                    new_location = f"{base_path}.csv"
                    df.to_csv(new_location, index=False, encoding='utf-8')
                    return new_location
                elif target_ext == 'xlsx':
                    new_location = f"{base_path}.xlsx"
                    df.to_excel(new_location, index=False)
                    return new_location
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Не вдалося конвертувати таблицю з {ext} у формат {target_ext}."
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Помилка під час обробки таблиці. Лог: {str(e)}"
                )
        
        return file_location

    else:
        if (
            options.resize
            or options.grayscale
            or options.flip
            or options.convert_to
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Обробка або конвертація для формату {ext} поки що не підтримується.",
            )
        return file_location
