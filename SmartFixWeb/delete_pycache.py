from pathlib import Path, PosixPath

def delete_pycache_rec(target_directory : PosixPath) :
    for pycache_dir in target_directory.rglob('__pycache__'):
        try:
            for included_file in pycache_dir.iterdir():
                included_file.unlink() 
                
            pycache_dir.rmdir()  
            
        except Exception as e:
            print(f"Erreur lors de la suppression de {pycache_dir} : {e}")

if __name__ == "__main__" :
    current_directory = Path(__file__).parent
    delete_pycache_rec(current_directory)
