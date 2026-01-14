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
- **GitHub Pages**: [Веб-сайт](https://pioh.github.io/doc/)
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
        
        def find_target_chapter(section, chapter_num):
            """Находит главу по номеру раздела и главы"""
            for ch in self.chapters:
                if ch['section_num'] == section.zfill(2) and ch['chapter_num'] == chapter_num.zfill(2):
                    return ch
            return None
        
        # 1. Обработка **Глава X.Y** (жирные без ссылок)
        def replace_bold_chapter(match):
            section = match.group(1)
            chapter_num = match.group(2)
            target = find_target_chapter(section, chapter_num)
            if not target:
                return match.group(0)
            link_url = f"{target['section_num']}_{target['chapter_num']}_{target['slug']}.md"
            return f"[**Глава {section}.{chapter_num}**]({link_url})"
        
        content = re.sub(r'\*\*Глава (\d+)\.(\d+)\*\*(?!\])', replace_bold_chapter, content)
        
        # 2. Обработка [Глава X.Y] без ссылки после (не [Глава X.Y](...))
        def replace_bracket_chapter(match):
            section = match.group(1)
            chapter_num = match.group(2)
            target = find_target_chapter(section, chapter_num)
            if not target:
                return match.group(0)
            link_url = f"{target['section_num']}_{target['chapter_num']}_{target['slug']}.md"
            return f"[Глава {section}.{chapter_num}]({link_url})"
        
        content = re.sub(r'\[Глава (\d+)\.(\d+)\](?!\()', replace_bracket_chapter, content)
        
        # 3. Обработка обычных упоминаний: Глава/глава/главе X.Y (не в ссылках)
        def replace_plain_chapter(match):
            case_word = match.group(1)  # Глава/глава/главе/главы
            section = match.group(2)
            chapter_num = match.group(3)
            target = find_target_chapter(section, chapter_num)
            if not target:
                return match.group(0)
            link_url = f"{target['section_num']}_{target['chapter_num']}_{target['slug']}.md"
            return f"[{case_word} {section}.{chapter_num}]({link_url})"
        
        content = re.sub(r'(?<!\[|\*)([Гг]лав[аеуы]) (\d+)\.(\d+)(?!\])', replace_plain_chapter, content)
        
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
        
        # Создаём index.html для Docsify с уменьшенными отступами
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
      --base-font-size: 15px;
      --theme-color: #0074d9;
    }
    
    /* ========== Сайдбар как в PDF viewer ========== */
    .sidebar {
      padding: 15px 10px !important;
      background: #f8f9fa !important;
      border-right: 1px solid #e1e4e8 !important;
    }
    
    /* Убираем большой заголовок */
    .sidebar > h1 {
      display: none !important;
    }
    
    .app-name {
      display: none !important;
    }
    
    /* Компактное дерево оглавления */
    .sidebar ul {
      padding: 0 !important;
      margin: 0 !important;
    }
    
    .sidebar ul li {
      padding: 0 !important;
      margin: 0 !important;
      line-height: 1.6 !important;
      list-style: none !important;
    }
    
    /* Разделы (жирные, без отступа) */
    .sidebar ul li strong {
      display: block;
      padding: 8px 5px 4px 5px !important;
      font-size: 13px !important;
      color: #24292e !important;
      font-weight: 600 !important;
      border-bottom: 1px solid #e1e4e8;
      margin-top: 12px !important;
    }
    
    .sidebar ul li:first-child strong {
      margin-top: 0 !important;
    }
    
    /* Главы (с отступом) */
    .sidebar ul li a {
      display: block !important;
      padding: 5px 5px 5px 15px !important;
      font-size: 13px !important;
      color: #586069 !important;
      text-decoration: none !important;
      border-radius: 3px !important;
      transition: all 0.2s !important;
    }
    
    /* Ховер на главах */
    .sidebar ul li a:hover {
      background: #e8eaed !important;
      color: #0366d6 !important;
    }
    
    /* АКТИВНАЯ глава (текущая страница) */
    .sidebar ul li.active > a {
      background: #0074d9 !important;
      color: #fff !important;
      font-weight: 600 !important;
    }
    
    /* Скрытие сайдбара на мобильных */
    @media screen and (max-width: 768px) {
      .sidebar {
        transform: translateX(-300px);
      }
      
      .sidebar.open {
        transform: translateX(0);
      }
    }
    
    /* ========== Контент ========== */
    .markdown-section {
      max-width: 90% !important;
      padding: 20px 30px 40px 30px !important;
    }
    
    /* Компактные заголовки */
    .markdown-section h1 {
      margin: 2rem 0 1rem !important;
      font-size: 2em !important;
    }
    
    .markdown-section h2 {
      margin: 1.5rem 0 0.8rem !important;
      font-size: 1.5em !important;
    }
    
    .markdown-section h3 {
      margin: 1.2rem 0 0.6rem !important;
      font-size: 1.25em !important;
    }
    
    .markdown-section h4 {
      margin: 1rem 0 0.5rem !important;
      font-size: 1.1em !important;
    }
    
    /* Компактные параграфы */
    .markdown-section p {
      margin: 0.6em 0 !important;
      line-height: 1.6 !important;
    }
    
    /* Компактные списки */
    .markdown-section ul,
    .markdown-section ol {
      margin: 0.6em 0 !important;
      padding-left: 1.5em !important;
    }
    
    .markdown-section li {
      margin: 0.3em 0 !important;
    }
    
    /* Компактные блоки кода */
    .markdown-section pre {
      margin: 1em 0 !important;
      padding: 1em !important;
    }
    
    .markdown-section code {
      padding: 2px 4px !important;
    }
  </style>
</head>
<body>
  <div id="app">Загрузка...</div>
  <script>
    window.$docsify = {
      name: '',  // Убираем название, чтобы не занимало место
      repo: '',
      loadSidebar: true,
      subMaxLevel: 3,
      auto2top: true,
      alias: {
        '/.*/_sidebar.md': '/_sidebar.md'
      },
      search: {
        placeholder: 'Поиск...',
        noData: 'Ничего не найдено',
        depth: 6
      },
      pagination: {
        previousText: '← Предыдущая',
        nextText: 'Следующая →'
      },
      // Автоматическая подсветка активного раздела
      sidebarDisplayLevel: 1,
      
      // Плагин для добавления заголовка в сайдбар
      plugins: [
        function(hook, vm) {
          // Добавляем компактный заголовок в начало сайдбара
          hook.mounted(function() {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar && !document.querySelector('.sidebar-title')) {
              const title = document.createElement('div');
              title.className = 'sidebar-title';
              title.innerHTML = '<strong>📚 Учебник по информатике</strong>';
              title.style.cssText = 'padding: 10px 5px 15px 5px; font-size: 14px; color: #24292e; border-bottom: 2px solid #0074d9; margin-bottom: 10px;';
              sidebar.insertBefore(title, sidebar.firstChild);
            }
          });
        }
      ]
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
        
        # Создаём _sidebar.md для Docsify (компактное дерево оглавления)
        sidebar_content = ""
        
        for section_num, section_data in self.toc_structure.items():
            # Раздел как подзаголовок (не кликабельный)
            sidebar_content += f"* **{int(section_num)}. {section_data['name']}**\n"
            
            for chapter in section_data['chapters']:
                link = f"/book/{chapter['section_num']}_{chapter['chapter_num']}_{chapter['slug']}.md"
                # Главы с отступом
                sidebar_content += f"  * [{chapter['full_num']} {chapter['title']}]({link})\n"
        
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
            margin: 1.2cm;
            @bottom-center {{
                content: counter(page);
                font-size: 9pt;
            }}
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #000;
        }}
        
        h1 {{
            font-size: 14pt;
            font-weight: bold;
            text-align: center;
            margin-top: 0;
            margin-bottom: 0.7cm;
            page-break-before: always;
            page-break-after: avoid;
        }}
        
        h1:first-of-type {{
            page-break-before: avoid;
        }}
        
        h2 {{
            font-size: 11pt;
            font-weight: bold;
            margin-top: 0.6cm;
            margin-bottom: 0.3cm;
            page-break-after: avoid;
        }}
        
        h3 {{
            font-size: 10pt;
            font-weight: bold;
            margin-top: 0.5cm;
            margin-bottom: 0.2cm;
            page-break-after: avoid;
        }}
        
        h4 {{
            font-size: 10pt;
            font-weight: bold;
            font-style: italic;
            margin-top: 0.4cm;
            margin-bottom: 0.15cm;
            page-break-after: avoid;
        }}
        
        p {{
            text-align: justify;
            margin-bottom: 0.3cm;
        }}
        
        code {{
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            background-color: #f5f5f5;
            padding: 1px 3px;
        }}
        
        pre {{
            font-family: 'Courier New', monospace;
            font-size: 8pt;
            background-color: #f5f5f5;
            padding: 6px;
            border-left: 2px solid #ccc;
            overflow-x: auto;
            white-space: pre-wrap;
            margin: 0.3cm 0;
        }}
        
        ul, ol {{
            margin-left: 0.6cm;
            margin-bottom: 0.3cm;
        }}
        
        li {{
            margin-bottom: 0.1cm;
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
            font-size: 20pt;
            page-break-before: avoid;
        }}
        
        .title-page p {{
            font-size: 12pt;
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
            margin-top: 0.4cm;
            font-weight: bold;
            font-size: 11pt;
        }}
        
        .toc-chapter {{
            margin-left: 0.5cm;
            margin-top: 0.15cm;
            font-size: 10pt;
        }}
        
        .toc-subchapter {{
            margin-left: 1cm;
            margin-top: 0.1cm;
            font-size: 9pt;
            color: #333;
        }}
        
        .chapter {{
            page-break-before: always;
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
        
        # Оглавление с подразделами
        for section_num, section_data in self.toc_structure.items():
            html_content += f'<div class="toc-section">Раздел {int(section_num)}: {section_data["name"]}</div>\n'
            
            for chapter in section_data['chapters']:
                chapter_id = f"chapter_{chapter['section_num']}_{chapter['chapter_num']}"
                html_content += f'<div class="toc-chapter">{chapter["full_num"]}. <a href="#{chapter_id}">{chapter["title"]}</a></div>\n'
                
                # Добавляем подразделы (## заголовки)
                try:
                    with open(chapter['path'], 'r', encoding='utf-8') as f:
                        chapter_content = f.read()
                    
                    # Ищем заголовки уровня 2 (##)
                    h2_pattern = r'^## (.+)$'
                    h2_matches = re.finditer(h2_pattern, chapter_content, re.MULTILINE)
                    
                    for i, match in enumerate(h2_matches):
                        h2_title = match.group(1).strip()
                        # Пропускаем служебные заголовки
                        if h2_title.lower() in ['введение', 'ключевые термины', 'контрольные вопросы', 'резюме', 'связь с другими темами', 'связь с другими главами']:
                            continue
                        h2_id = f"{chapter_id}_h2_{i}"
                        html_content += f'<div class="toc-subchapter"><a href="#{h2_id}">{h2_title}</a></div>\n'
                except:
                    pass  # Если не удалось прочитать главу, пропускаем
        
        html_content += "</div>\n\n"
        
        # Главы с bookmarks для PDF
        for chapter in self.chapters:
            source_path = chapter['path']
            
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Конвертируем ссылки на главы в относительные якоря
            def convert_pdf_links(match):
                section = match.group(1)
                chapter_num = match.group(2)
                target_id = f"chapter_{section.zfill(2)}_{chapter_num.zfill(2)}"
                link_text = f"Глава {section}.{chapter_num}"
                return f'<a href="#{target_id}">{link_text}</a>'
            
            # Заменяем [Глава X.Y](...) на внутренние ссылки
            content = re.sub(r'\[Глава (\d+)\.(\d+)\]\([^)]+\)', convert_pdf_links, content)
            content = re.sub(r'\[\*\*Глава (\d+)\.(\d+)\*\*\]\([^)]+\)', lambda m: f'<a href="#chapter_{m.group(1).zfill(2)}_{m.group(2).zfill(2)}"><strong>Глава {m.group(1)}.{m.group(2)}</strong></a>', content)
            
            # Конвертируем markdown в HTML с якорями для подразделов
            md = markdown.Markdown(extensions=['extra', 'codehilite', 'tables', 'toc', 'attr_list'])
            html_chapter = md.convert(content)
            
            # Добавляем ID к подразделам
            chapter_id = f"chapter_{chapter['section_num']}_{chapter['chapter_num']}"
            h2_counter = 0
            
            def add_h2_id(match):
                nonlocal h2_counter
                h2_id = f'{chapter_id}_h2_{h2_counter}'
                h2_counter += 1
                return f'<h2 id="{h2_id}">{match.group(1)}</h2>'
            
            html_chapter = re.sub(r'<h2>(.+?)</h2>', add_h2_id, html_chapter)
            
            # Добавляем главу с классом для page-break
            html_content += f'<div class="chapter" id="{chapter_id}">\n{html_chapter}\n</div>\n\n'
        
        html_content += "</body></html>"
        
        # Генерируем PDF через WeasyPrint с bookmarks
        pdf_path = self.root_dir / "учебник_информатика.pdf"
        
        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            font_config = FontConfiguration()
            
            # CSS для добавления bookmarks (встроенного оглавления PDF)
            bookmark_css = CSS(string='''
                h1 { bookmark-level: 1; bookmark-label: content(); }
                h2 { bookmark-level: 2; bookmark-label: content(); }
                h3 { bookmark-level: 3; bookmark-label: content(); }
            ''')
            
            HTML(string=html_content).write_pdf(
                pdf_path,
                stylesheets=[bookmark_css],
                font_config=font_config
            )
            print(f"  ✅ PDF создан: {pdf_path}")
            print(f"  ✅ Добавлено встроенное оглавление (bookmarks)")
            
            # Показываем размер
            size_mb = pdf_path.stat().st_size / (1024 * 1024)
            print(f"  📊 Размер: {size_mb:.2f} МБ")
            return True
        except Exception as e:
            print(f"  ❌ Ошибка при создании PDF: {e}")
            import traceback
            traceback.print_exc()
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
