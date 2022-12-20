from multiprocessing import Pool, cpu_count

__global_pool = None

def get_global_pool() -> Pool:
    global __global_pool
    if __global_pool == None:
        __global_pool = Pool(cpu_count())
    return __global_pool