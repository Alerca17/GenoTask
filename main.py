from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import random
import copy

app = FastAPI(title="Distribuidor de Tareas IA")

# Montar la carpeta estática para el Frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- DATOS SIMULADOS ---
WORKERS = [
    {"id": 0, "name": "Ana (Dev Senior)", "skill": 1.5, "max_load": 4},
    {"id": 1, "name": "Alejo (AI Engineer)", "skill": 1.8, "max_load": 4},
    {"id": 2, "name": "Carlos (Junior)", "skill": 0.8, "max_load": 3}
]

TASKS = [
    {"id": 0, "name": "Diseñar Base de Datos", "difficulty": 10},
    {"id": 1, "name": "Crear UI/UX", "difficulty": 8},
    {"id": 2, "name": "Programar Algoritmo", "difficulty": 15},
    {"id": 3, "name": "Escribir Documentación", "difficulty": 5},
    {"id": 4, "name": "Configurar Servidor", "difficulty": 12},
    {"id": 5, "name": "Testing Unitario", "difficulty": 7},
    {"id": 6, "name": "Revisión de Seguridad", "difficulty": 10},
    {"id": 7, "name": "Optimización de Consultas", "difficulty": 9}
]

# --- LÓGICA DEL ALGORITMO GENÉTICO ---
def calculate_fitness(chromosome):
    worker_times = {w["id"]: 0 for w in WORKERS}
    worker_loads = {w["id"]: 0 for w in WORKERS}
    
    for task_idx, worker_id in enumerate(chromosome):
        task = TASKS[task_idx]
        worker = next(w for w in WORKERS if w["id"] == worker_id)
        
        # Tiempo = Dificultad de la tarea / Habilidad del trabajador
        time_taken = task["difficulty"] / worker["skill"]
        worker_times[worker_id] += time_taken
        worker_loads[worker_id] += 1
        
    makespan = max(worker_times.values()) # Tiempo total del proyecto (el que más tarda)
    
    # Penalización si se le asignan demasiadas tareas a una sola persona
    penalty = sum(50 for w in WORKERS if worker_loads[w["id"]] > w["max_load"])
    
    return 1.0 / (makespan + penalty + 1e-6) # Queremos maximizar esto

def create_population(pop_size, num_tasks, num_workers):
    return [[random.randint(0, num_workers - 1) for _ in range(num_tasks)] for _ in range(pop_size)]

def mutate(chromosome, mutation_rate, num_workers):
    for i in range(len(chromosome)):
        if random.random() < mutation_rate:
            chromosome[i] = random.randint(0, num_workers - 1)
    return chromosome

def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.post("/optimize")
def run_genetic_algorithm():
    pop_size = 100
    generations = 200
    mutation_rate = 0.1
    num_tasks = len(TASKS)
    num_workers = len(WORKERS)
    
    population = create_population(pop_size, num_tasks, num_workers)
    
    for _ in range(generations):
        # Evaluar
        fitness_scores = [(chrom, calculate_fitness(chrom)) for chrom in population]
        fitness_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Selección (los mejores pasan directo)
        new_population = [x[0] for x in fitness_scores[:10]]
        
        # Cruce y Mutación para llenar el resto
        while len(new_population) < pop_size:
            p1, p2 = random.choices(fitness_scores[:30], k=2) # Torneo simple
            c1, c2 = crossover(p1[0], p2[0])
            new_population.extend([mutate(c1, mutation_rate, num_workers), mutate(c2, mutation_rate, num_workers)])
            
        population = new_population[:pop_size]

    # Obtener el mejor resultado final
    best_chromosome = fitness_scores[0][0]
    
    # Formatear la respuesta para el Front
    result = {w["name"]: [] for w in WORKERS}
    total_time_per_worker = {w["name"]: 0 for w in WORKERS}
    
    for task_idx, worker_id in enumerate(best_chromosome):
        worker = next(w for w in WORKERS if w["id"] == worker_id)
        task = TASKS[task_idx]
        time_taken = round(task["difficulty"] / worker["skill"], 2)
        result[worker["name"]].append({"task": task["name"], "time": time_taken})
        total_time_per_worker[worker["name"]] += time_taken
        
    return {
        "assignments": result,
        "metrics": {k: round(v, 2) for k, v in total_time_per_worker.items()},
        "total_project_time": round(max(total_time_per_worker.values()), 2)
    }