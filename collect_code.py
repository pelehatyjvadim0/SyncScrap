import os

# Конфиг: что пропускаем
EXCLUDE_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'env', '.idea', '.vscode'}
EXCLUDE_FILES = {'collect_code.py', '.DS_Store'}
EXTENSIONS = {'.py'} # Можешь добавить '.env', '.yaml', если нужно

def collect_project_code(root_dir, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(root_dir):
            # Фильтруем папки
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file in EXCLUDE_FILES or not any(file.endswith(ext) for ext in EXTENSIONS):
                    continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_dir)
                
                f.write(f"\n{'='*80}\n")
                f.write(f"FILE: {rel_path}\n")
                f.write(f"{'='*80}\n\n")
                
                try:
                    with open(full_path, 'r', encoding='utf-8') as code_file:
                        f.write(code_file.read())
                except Exception as e:
                    f.write(f"Ошибка чтения файла: {e}")
                f.write("\n\n")

if __name__ == "__main__":
    output = "project_code_for_review.txt"
    collect_project_code('.', output)
    print(f"Готово! Весь код собран в файл: {output}")