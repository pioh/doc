#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт сборки учебника по информатике

Создаёт:
1. README.md в корне с оглавлением и ссылками
2. /book/ с MD-файлами для GitHub (с кликабельными ссылками между главами)
3. Настройку GitHub Pages (Docsify)
4. PDF с оглавлением и рабочими ссылками
5. .gitattributes для пометки автогенерированных файлов

Использование:
    python build_script.py
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

# Проверка зависимостей
try:
    import markdown
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError as e:
    print("❌ ОШИБКА: Не установлены необходимые библиотеки")
    print("\nУстановите зависимости:")
    print("  pip install markdown weasyprint")
    print("\nТакже требуется установить системные пакеты для WeasyPrint:")
    print("  Manjaro/Arch: sudo pacman -S pango cairo")
    exit(1)


class TextbookBuilder:
    """Класс для сборки учебника в разные форматы"""
    
    def __init__(self, chapters_dir="chapters", output_dir="book"):
        self.chapters_dir = Path(chapters_dir)
        self.output_dir = Path(output_dir)
        self.root_dir = Path(".")
        self.chapters = []
        self.toc_structure = OrderedDict()
        
    def parse_chapters(self):
        """Парсинг всех глав и построение структуры"""
        print("\n📚 Парсинг структуры глав...")
        
        if not self.chapters_dir.exists():
            print(f"❌ ОШИБКА: Папка {self.chapters_dir} не найдена!")
            return False
        
        # Структура разделов (из spec.md)
        sections = {
            "01": "Понятие информации",
            "02": "Технические средства",
            "03": "Программные средства",
            "04": "Модели решения задач",
            "05": "Основы алгоритмизации",
            "06": "Языки программирования",
            "07": "Базы данных",
            "08": "Локальные и глобальные сети",
            "09": "Защита информации"
        }
        
        chapter_files = sorted(self.chapters_dir.glob("*.md"))
        
        for chapter_file in chapter_files:
            # Парсим имя файла: 01_02_название.md
            match = re.match(r'(\d{2})_(\d{2})_(.+)\.md', chapter_file.name)
            if not match:
                continue
                
            section_num = match.group(1)
            chapter_num = match.group(2)
            chapter_slug = match.group(3)
            
            # Читаем заголовок главы
            try:
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('# '):
                        title = first_line[2:].strip()
                        # Убираем "Глава X.Y: " если есть
                        title = re.sub(r'^Глава \d+\.\d+[:\s]*', '', title)
                    else:
                        title = chapter_slug.replace('_', ' ').title()
            except:
                title = chapter_slug.replace('_', ' ').title()
            
            chapter_info = {
                'section_num': section_num,
                'chapter_num': chapter_num,
                'full_num': f"{int(section_num)}.{int(chapter_num)}",
                'slug': chapter_slug,
                'title': title,
                'filename': chapter_file.name,
                'path': chapter_file
            }
            
            self.chapters.append(chapter_info)
            
            # Добавляем в структуру оглавления
            section_name = sections.get(section_num, f"Раздел {int(section_num)}")
            if section_num not in self.toc_structure:
                self.toc_structure[section_num] = {
                    'name': section_name,
                    'chapters': []
                }
            self.toc_structure[section_num]['chapters'].append(chapter_info)
        
        print(f"  ✅ Найдено {len(self.chapters)} глав в {len(self.toc_structure)} разделах")
        return True
    
    def generate_root_readme(self):
        """Генерация README.md в корне с оглавлением"""
        print("\n📝 Генерация README.md...")
        
        readme_content = f"""# Учебник по информатике

**Для студентов первого курса технических специальностей**

Полный курс информатики, охватывающий все основные темы: от систем счисления до информационной безопасности.

---

## 📖 Как читать

- **GitHub**: [Онлайн версия](/book/) (оглавление ниже)
- **GitHub Pages**: [Веб-сайт](https://tema.github.io/doc/) *(если настроен)*
- **PDF**: [Скачать учебник](./учебник_информатика.pdf)

---

## 📚 Оглавление

"""
        
        for section_num, section_data in self.toc_structure.items():
            readme_content += f"\n### Раздел {int(section_num)}: {section_data['name']}\n\n"
            
            for chapter in section_data['chapters']:
                # Ссылка на файл в /book/
                link = f"/book/{chapter['section_num']}_{chapter['chapter_num']}_{chapter['slug']}.md"
                readme_content += f"{int(chapter['chapter_num'])}. [**{chapter['title']}**]({link})\n"
        
        readme_content += f"""
---

## 📊 Статистика

- **Всего глав**: {len(self.chapters)}
- **Разделов**: {len(self.toc_structure)}
- **Последнее обновление**: {datetime.now().strftime('%d.%m.%Y')}

---

## 🛠️ Для разработчиков

Структура проекта:

```
/
├── README.md              # Это оглавление
├── book/                  # Главы для GitHub (автогенерация)
├── учебник_информатика/   # Исходники
│   ├── chapters/         # Markdown-файлы глав
│   ├── build_script.py   # Скрипт сборки
│   └── ...
└── учебник_информатика.pdf # Итоговый PDF
```

Для пересборки:

```bash
cd учебник_информатика
python build_script.py
```

---

## 📜 Лицензия

Учебник создан для образовательных целей.

---

*Автоматически сгенерировано скриптом build_script.py*
"""
        
        readme_path = self.root_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"  ✅ Создан: {readme_path}")
        return True
    
    def convert_chapter_links(self, content, current_chapter):
        """Конвертация упоминаний глав в кликабельные ссылки"""
        
        # Паттерны для поиска упоминаний глав:
        # - "Глава 1.2", "глава 1.2", "главе 1.2"
        # - "Глава 1.2 (Название)"
        # - "**Глава 1.2**"
        
        def replace_chapter_mention(match):
            full_match = match.group(0)
            section = match.group(1)
            chapter = match.group(2)
            
            # Находим главу в списке
            target_chapter = None
            for ch in self.chapters:
                if ch['section_num'] == section.zfill(2) and ch['chapter_num'] == chapter.zfill(2):
                    target_chapter = ch
                    break
            
            if not target_chapter:
                return full_match  # Не нашли - оставляем как есть
            
            # Создаём ссылку
            link_text = f"Глава {section}.{chapter}"
            link_url = f"{target_chapter['section_num']}_{target_chapter['chapter_num']}_{target_chapter['slug']}.md"
            
            # Сохраняем окружающее форматирование
            if '**' in full_match:
                return f"[**{link_text}**]({link_url})"
            else:
                return f"[{link_text}]({link_url})"
        
        # Ищем упоминания глав
        patterns = [
            r'\*\*Глава (\d+)\.(\d+)\*\*',  # **Глава 1.2**
            r'[Гг]лав[аеуы] (\d+)\.(\d+)',  # Глава 1.2, главе 1.2, и т.д.
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, replace_chapter_mention, content)
        
        return content
    
    def export_book_markdown(self):
        """Экспорт глав в /book/ с конвертацией ссылок"""
        print("\n📁 Экспорт глав в /book/...")
        
        # Создаём папку /book/
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir()
        
        # Создаём README.md для /book/
        book_readme = f"""# Учебник по информатике

[← Вернуться к главному оглавлению](../README.md)

---

## Оглавление

"""
        
        for section_num, section_data in self.toc_structure.items():
            book_readme += f"\n### Раздел {int(section_num)}: {section_data['name']}\n\n"
            
            for chapter in section_data['chapters']:
                link = f"{chapter['section_num']}_{chapter['chapter_num']}_{chapter['slug']}.md"
                book_readme += f"{int(chapter['chapter_num'])}. [{chapter['title']}]({link})\n"
        
        book_readme += "\n---\n\n*Автоматически сгенерировано*\n"
        
        with open(self.output_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(book_readme)
        
        # Копируем и конвертируем каждую главу
        for chapter in self.chapters:
            source_path = chapter['path']
            target_filename = f"{chapter['section_num']}_{chapter['chapter_num']}_{chapter['slug']}.md"
            target_path = self.output_dir / target_filename
            
            # Читаем исходный файл
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Конвертируем ссылки на главы
            content = self.convert_chapter_links(content, chapter)
            
            # Добавляем шапку с навигацией
            nav_header = f"""[← К оглавлению](README.md)

---

"""
            content = nav_header + content
            
            # Добавляем футер
            footer = f"""

---

[← К оглавлению](README.md)

*Глава {chapter['full_num']}: {chapter['title']}*
"""
            content = content + footer
            
            # Сохраняем
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ {target_filename}")
        
        print(f"\n  ✅ Экспортировано {len(self.chapters)} глав в /book/")
        return True
    
    def setup_github_pages(self):
        """Настройка GitHub Pages с Docsify"""
        print("\n🌐 Настройка GitHub Pages (Docsify)...")
        
        # Создаём index.html для Docsify
        index_html = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Учебник по информатике</title>
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
  <meta name="description" content="Полный курс информатики для первокурсников">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">
  <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/vue.css">
  <style>
    :root {
      --base-font-size: 16px;
      --theme-color: #0074d9;
    }
  </style>
</head>
<body>
  <div id="app">Загрузка...</div>
  <script>
    window.$docsify = {
      name: 'Учебник по информатике',
      repo: '',
      loadSidebar: true,
      subMaxLevel: 3,
      auto2top: true,
      search: {
        placeholder: 'Поиск...',
        noData: 'Ничего не найдено',
        depth: 6
      },
      pagination: {
        previousText: '← Предыдущая',
        nextText: 'Следующая →'
      }
    }
  </script>
  <!-- Docsify core -->
  <script src="//cdn.jsdelivr.net/npm/docsify@4"></script>
  <!-- Поиск -->
  <script src="//cdn.jsdelivr.net/npm/docsify/lib/plugins/search.min.js"></script>
  <!-- Пагинация -->
  <script src="//cdn.jsdelivr.net/npm/docsify-pagination/dist/docsify-pagination.min.js"></script>
</body>
</html>
"""
        
        with open(self.root_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        # Создаём _sidebar.md для Docsify
        sidebar_content = "**Учебник по информатике**\n\n"
        
        for section_num, section_data in self.toc_structure.items():
            sidebar_content += f"* **Раздел {int(section_num)}: {section_data['name']}**\n"
            
            for chapter in section_data['chapters']:
                link = f"/book/{chapter['section_num']}_{chapter['chapter_num']}_{chapter['slug']}.md"
                sidebar_content += f"  * [{chapter['full_num']} {chapter['title']}]({link})\n"
            
            sidebar_content += "\n"
        
        with open(self.root_dir / "_sidebar.md", 'w', encoding='utf-8') as f:
            f.write(sidebar_content)
        
        print("  ✅ Создан index.html")
        print("  ✅ Создан _sidebar.md")
        print("\n  ℹ️  Для запуска локально: python -m http.server 3000")
        print("  ℹ️  Откройте http://localhost:3000")
        return True
    
    def generate_pdf(self):
        """Генерация PDF с оглавлением и ссылками"""
        print("\n📄 Генерация PDF...")
        
        # Собираем HTML-контент
        html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Учебник по информатике</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
            @bottom-center {{
                content: counter(page);
            }}
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 1.5;
            color: #000;
        }}
        
        h1 {{
            font-size: 18pt;
            font-weight: bold;
            text-align: center;
            margin-top: 2cm;
            margin-bottom: 1cm;
            page-break-before: always;
        }}
        
        h1:first-of-type {{
            page-break-before: avoid;
        }}
        
        h2 {{
            font-size: 14pt;
            font-weight: bold;
            margin-top: 1cm;
            margin-bottom: 0.5cm;
        }}
        
        h3 {{
            font-size: 12pt;
            font-weight: bold;
            margin-top: 0.7cm;
            margin-bottom: 0.3cm;
        }}
        
        h4 {{
            font-size: 12pt;
            font-weight: bold;
            margin-top: 0.5cm;
            margin-bottom: 0.2cm;
        }}
        
        p {{
            text-align: justify;
            margin-bottom: 0.5cm;
        }}
        
        code {{
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            background-color: #f5f5f5;
            padding: 2px 4px;
        }}
        
        pre {{
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            background-color: #f5f5f5;
            padding: 10px;
            border-left: 3px solid #ccc;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        
        ul, ol {{
            margin-left: 1cm;
        }}
        
        li {{
            margin-bottom: 0.2cm;
        }}
        
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        
        strong {{
            font-weight: bold;
        }}
        
        .title-page {{
            text-align: center;
            margin-top: 5cm;
        }}
        
        .title-page h1 {{
            font-size: 24pt;
            page-break-before: avoid;
        }}
        
        .title-page p {{
            font-size: 14pt;
            margin-top: 1cm;
        }}
        
        .toc {{
            page-break-after: always;
        }}
        
        .toc h1 {{
            text-align: center;
            page-break-before: avoid;
        }}
        
        .toc-section {{
            margin-top: 0.5cm;
            font-weight: bold;
        }}
        
        .toc-chapter {{
            margin-left: 0.5cm;
            margin-top: 0.2cm;
        }}
    </style>
</head>
<body>
    <div class="title-page">
        <h1>УЧЕБНИК ПО ИНФОРМАТИКЕ</h1>
        <p>Для студентов первого курса технических специальностей</p>
        <p style="margin-top: 3cm;">{datetime.now().year}</p>
    </div>
    
    <div class="toc">
        <h1>ОГЛАВЛЕНИЕ</h1>
"""
        
        # Оглавление
        for section_num, section_data in self.toc_structure.items():
            html_content += f'<div class="toc-section">Раздел {int(section_num)}: {section_data["name"]}</div>\n'
            
            for chapter in section_data['chapters']:
                chapter_id = f"chapter_{chapter['section_num']}_{chapter['chapter_num']}"
                html_content += f'<div class="toc-chapter">{chapter["full_num"]}. <a href="#{chapter_id}">{chapter["title"]}</a></div>\n'
        
        html_content += "</div>\n\n"
        
        # Главы
        for chapter in self.chapters:
            source_path = chapter['path']
            
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Конвертируем markdown в HTML
            html_chapter = markdown.markdown(
                content,
                extensions=['extra', 'codehilite', 'tables', 'toc']
            )
            
            # Добавляем якорь для оглавления
            chapter_id = f"chapter_{chapter['section_num']}_{chapter['chapter_num']}"
            html_content += f'<div id="{chapter_id}">\n{html_chapter}\n</div>\n\n'
        
        html_content += "</body></html>"
        
        # Генерируем PDF через WeasyPrint
        pdf_path = self.root_dir / "учебник_информатика.pdf"
        
        try:
            font_config = FontConfiguration()
            HTML(string=html_content).write_pdf(
                pdf_path,
                font_config=font_config
            )
            print(f"  ✅ PDF создан: {pdf_path}")
            
            # Показываем размер
            size_mb = pdf_path.stat().st_size / (1024 * 1024)
            print(f"  📊 Размер: {size_mb:.2f} МБ")
            return True
        except Exception as e:
            print(f"  ❌ Ошибка при создании PDF: {e}")
            return False
    
    def create_gitattributes(self):
        """Создание .gitattributes для пометки автогенерированных файлов"""
        print("\n📝 Создание .gitattributes...")
        
        gitattributes_content = """# Автогенерированные файлы (создаются build_script.py)

# Главная страница
/README.md linguist-generated=true

# Книга для GitHub
/book/** linguist-generated=true

# GitHub Pages
/index.html linguist-generated=true
/_sidebar.md linguist-generated=true

# PDF
/учебник_информатика.pdf binary linguist-generated=true

# Исходники (не автогенерированные)
/учебник_информатика/chapters/** linguist-generated=false
/учебник_информатика/build_script.py linguist-generated=false
"""
        
        with open(self.root_dir / ".gitattributes", 'w', encoding='utf-8') as f:
            f.write(gitattributes_content)
        
        print("  ✅ Создан .gitattributes")
        return True
    
    def build(self):
        """Главная функция сборки"""
        print("=" * 70)
        print("🚀 СБОРКА УЧЕБНИКА ПО ИНФОРМАТИКЕ")
        print("=" * 70)
        
        steps = [
            ("Парсинг глав", self.parse_chapters),
            ("Генерация README.md", self.generate_root_readme),
            ("Экспорт в /book/", self.export_book_markdown),
            ("Настройка GitHub Pages", self.setup_github_pages),
            ("Генерация PDF", self.generate_pdf),
            ("Создание .gitattributes", self.create_gitattributes),
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n❌ Ошибка на этапе: {step_name}")
                return False
        
        print("\n" + "=" * 70)
        print("✅ СБОРКА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 70)
        
        print("\n📦 Что создано:")
        print("  ✅ README.md — оглавление для GitHub")
        print("  ✅ /book/ — главы с кликабельными ссылками")
        print("  ✅ index.html + _sidebar.md — GitHub Pages (Docsify)")
        print("  ✅ учебник_информатика.pdf — итоговый PDF")
        print("  ✅ .gitattributes — пометка автогенерированных файлов")
        
        print("\n🌐 Для просмотра локально:")
        print("  python -m http.server 3000")
        print("  Откройте: http://localhost:3000")
        
        print("\n📤 Готово к коммиту в Git!")
        
        return True


def main():
    """Главная функция"""
    # Проверка текущей директории
    if not Path("spec.md").exists():
        print("❌ ОШИБКА: Запустите скрипт из папки учебник_информатика/")
        return 1
    
    # Переход в корень git-репозитория
    os.chdir("..")
    
    # Создание и запуск сборщика
    builder = TextbookBuilder(
        chapters_dir="учебник_информатика/chapters",
        output_dir="book"
    )
    
    success = builder.build()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
