import os

class Path_Manager():
    def __init__(self):
        self.working_directory = os.getcwd()
        self.repo_root_file = 'repo.root'
        # The root of the repo 
        self.repo_root_path = os.path.split(self.get_path_to(self.repo_root_file))[0]
        

    def get_path_to(self, d):
        current = self.working_directory
        prev = str()
        ret_path = os.path.join(current, d)
        # Recursively find repo.root 
        while not os.path.exists(ret_path) and not prev == current:
            prev = current
            current = os.path.split(current)[0]
            ret_path = os.path.join(current, d)
        
        if not prev == current:
            return ret_path
        else:
            raise Exception("Could not find path to " + d)

if __name__ == "__main__":
    pm = Path_Manager()
    print(pm.working_directory)
    print(pm.repo_root_path)
    print(pm.get_path_to('src'))
    try:
        pm.get_path_to('garbage')
    except:
        print('failed as expected for garbage')
    print(pm.get_path_to(os.path.join('keys', 'expired_filter.keys.json')))
    pass

