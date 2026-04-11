import os

# Список папок и файлов, которые нужно игнорировать
EXCLUDE_DIRS = {'.git', '__pycache__', '.venv', 'venv', '.pytest_cache', '.idea', '.vscode'}
EXCLUDE_FILES = {'project_to_txt.py', 'dump_project.txt', '.env'}
# Расширения файлов, которые мы хотим собрать
INCLUDE_EXTENSIONS = {'.py', '.ini', '.yaml', '.yml', '.toml', '.sql'}

def generate_project_dump(root_dir, output_file):
    with open(output_file, 'w', encoding='utf-8') as out:
        for root, dirs, files in os.walk(root_dir):
            # Фильтруем папки
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file in EXCLUDE_FILES:
                    continue
                
                if any(file.endswith(ext) for ext in INCLUDE_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, root_dir)
                    
                    out.write(f"\n{'='*80}\n")
                    out.write(f"FILE: {relative_path}\n")
                    out.write(f"{'='*80}\n\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            out.write(f.read())
                    except Exception as e:
                        out.write(f"Error reading file: {e}")
                    out.write("\n")

if __name__ == "__main__":
    # Запускаем в текущей директории
    current_dir = os.getcwd()
    output_name = "dump_project.txt"
    
    print(f"Собираю проект из {current_dir}...")
    generate_project_dump(current_dir, output_name)
    print(f"Готово! Весь код сохранен в файл: {output_name}")