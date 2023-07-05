import flet as ft
import os
import glob
from mutagen.id3 import ID3, TALB
from slugify import slugify


def main(page: ft.Page):
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.path:
            pair_operation_label.value = ''
            selected_files_paths.clear()
            pairs.clean()
            selected_files.clean()
            pairs.update()
            selected_files.update()
            pair_operation_label.update()
            files = glob.glob(f'{e.path}/*.mp3')
            operation_label.value = 'Выбранные файлы:'
            operation_label.update()
            selected_files_counter = 0
            for f in files:
                name = os.path.basename(f)
                selected_files_counter += 1
                selected_files.controls.append(ft.Text(f"{selected_files_counter}. {name}"))
                selected_files_paths.append(f)
            selected_files.update()
        else:
            operation_label.value = f'Отменено!'
            operation_label.update()

    def transliterate():
        custom_replacements = [['+', '_plus'], ['–', '-'], ['&', '_and_'], ['№', 'number']]
        if not selected_files_paths:
            operation_label.value = '⚠ Выберите папку с mp3 файлами!'
            operation_label.update()
        else:
            transliterated_counter = 0
            transliterated_files_path.clear()
            pairs_counter = 0
            operation_label.value = ""
            operation_label.update()
            selected_files.clean()
            pairs.clean()
            operation_label.value = f'Транслитерированные названия:'
            operation_label.update()
            operation_label.update()
            if create_pairs.value:
                pair_operation_label.value = f'Пары:'
                pair_operation_label.update()
            else:
                pair_operation_label.value = ''
                pair_operation_label.update()
            for path in selected_files_paths:
                base_folder_path = os.path.dirname(path)
                base_name = os.path.basename(path)
                audio = ID3(path)
                artist = slugify(
                    audio.get('TPE1').text[0],
                    separator='_',
                    replacements=custom_replacements)
                title = slugify(
                    audio.get('TIT2').text[0],
                    separator='_',
                    replacements=custom_replacements)
                new_name = f'{artist}_-_{title}.mp3'
                new_path = base_folder_path + f'/{new_name}'
                os.rename(path, new_path)
                transliterated_counter += 1
                selected_files.controls.append(ft.Text(f'{transliterated_counter}. {base_name} → {new_name}'))
                transliterated_files_path.append(new_path)

            operation_label.value = f'Транслитерированные названия | {transliterated_counter}/{len(selected_files.controls)}:'
            operation_label.update()
            selected_files.update()

            if create_pairs.value:
                minus_paths = []
                plus_paths = []
                for path in transliterated_files_path:
                    name = os.path.basename(path)
                    if '_plus.mp3' in name:
                        plus_paths.append(path)
                    else:
                        minus_paths.append(path)
                for plus_path in plus_paths:
                    plus_name = f'{os.path.basename(plus_path)}'
                    plus_name_simple = plus_name.replace('_plus.mp3', '')
                    for minus_path in minus_paths:
                        minus_name = f'{os.path.basename(minus_path)}'
                        if plus_name_simple in minus_name:
                            audio = ID3(minus_path)
                            audio['TALB'] = TALB(encoding=3, text=[plus_name])
                            audio.save()
                            pairs_counter += 1
                            pairs.controls.append(ft.Text(f"{pairs_counter}. {minus_name} : {plus_name}"))
                pair_operation_label.value = f'Пары | {pairs_counter}/{len(minus_paths)}:'
                pair_operation_label.update()
                pairs.update()

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    selected_files = ft.ListView(expand=True, spacing=10, height=384, width=float('inf'))
    pairs = ft.ListView(expand=True, spacing=10, height=364, width=float('inf'))
    operation_label = ft.Text()
    pair_operation_label = ft.Text()
    selected_files_paths = []
    transliterated_files_path = []
    page.overlay.append(pick_files_dialog)
    create_pairs = ft.Checkbox(label="Создавать пару", value=False)
    page.theme = ft.Theme(color_scheme_seed='green')
    page.add(
        ft.Container(
            ft.Stack(
                controls=[
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                'Открыть файлы',
                                icon=ft.icons.UPLOAD_FILE,
                                on_click=lambda _: pick_files_dialog.get_directory_path(),
                            ),
                            ft.ElevatedButton(
                                'Транслитерация',
                                icon=ft.icons.TRANSLATE,
                                on_click=lambda _: transliterate(),
                            ),
                            create_pairs
                        ]
                    ),
                ]
            ),
            padding=5,
            border_radius=8,
        ),
        ft.Row(controls=[
            operation_label,
        ]),
        ft.Container(ft.Stack([
            selected_files,

        ])),
        ft.Divider(height=9, thickness=3),
        ft.Row(controls=[
            pair_operation_label,
        ]),
        ft.Container(ft.Stack([
            pairs,
        ])),
    )


if __name__ == '__main__':
    ft.app(target=main)
