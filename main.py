import inquirer
import sys
import os
import json
from datetime import datetime
from pprint import pprint
# Rich imports
from rich import print
from rich.console import Console
from rich.table import Table

console = Console(width=100, color_system="truecolor")

def createTable():
  global table
  table = Table(title="TODO List")
  table.add_column("ID", justify="left", style="white", no_wrap=True)
  table.add_column("Nombre", justify="center", style="purple")
  table.add_column("Urgencia", justify="center", style="yellow")
  table.add_column("Fecha", justify="left", style="cyan")
  table.add_column("Status", justify="left", style="magenta")

createTable()

#Functions
def clearScreen():
  os.system("cls")

def printRule(text):
  console.rule(f"[bold purple]{text}[/bold purple]")
  print()

def readJSON():
  global json_string
  global json_object
  try:
    with open("data.json", "r") as file:
      json_string = file.read()
    json_object = json.loads(json_string)
  except:
    with open("data.json", "w") as file:
      file.write(json.dumps({}, indent=2))
    readJSON()

def saveJSON():
  with open("data.json", "w") as file:
    file.write(json.dumps(json_object, indent=2))

def inputTODO():
  global answers
  global formatted_date_str
  questions = [
    inquirer.Text("nombre", message="Nombre de la tarea"),
    inquirer.List("urgencia", message="Urgencia de la tarea",
                  choices=[
                    "Leve",
                    "Media",
                    "Grave"
                  ]),
    inquirer.Text("fecha", message="Fecha de vencimiento (ddmmYYYY)")
  ]
  answers = inquirer.prompt(questions)
  parsed_date = datetime.strptime(answers["fecha"], "%d%m%Y")
  formatted_date_str = parsed_date.strftime("%d-%m-%Y")

def añadir(usuario):
  clearScreen()
  printRule("Añadir Tarea")
  try:
    inputTODO()
    id = len(json_object[usuario]["TODO"]) + 1
    json_object[usuario]["TODO"][id] = {
      'id': id,
      'nombre': answers["nombre"],
      'urgencia': answers['urgencia'],
      'fecha': formatted_date_str,
      'status': '❌' 
    }
    saveJSON()
    console.print("[bold green]Tarea añadida con exito.[/bold green]\nPresione cualquier tecla para continuar . . .")
    input()
  except:
    console.print("[bold red]Oops...[/bold red] Algo salió mal, intentalo de nuevo.")
    input()

def modificar(usuario):
  clearScreen()
  printRule("Modificar TODO")
  try:
    id = inquirer.prompt([ inquirer.List("id", message="¿Qué tarea desea modificar?",
                                              choices=[(f"{index}. {json_object[usuario]["TODO"][index]["nombre"]}", index) for index in json_object[usuario]["TODO"]])])
    inputTODO()
    todoObject = json_object[usuario]["TODO"][id["id"]]
    todoObject["nombre"] = answers["nombre"] if len(answers["nombre"]) > 0 else todoObject["nombre"]
    todoObject["urgencia"] = answers["urgencia"]
    todoObject["fecha"] = formatted_date_str if len(formatted_date_str) > 0 else todoObject["fecha"]
    saveJSON()
    console.print("[bold green]Se ha modificado el todo con exito[/bold green]\nPresione cualquier tecla para continuar . . .")
    input()
  except:
    console.print("[bold red]Oops...[/bold red] Algo salió mal, intentalo de nuevo.")
    input()

def remove(usuario):
    clearScreen()
    printRule("Eliminar TODOs")

    # Generate choices for the checkbox prompt
    todo_choices = [(f"{index}. {json_object[usuario]['TODO'][index]['nombre']}", index) for index in json_object[usuario]['TODO']]

    answers = inquirer.prompt([
        inquirer.Checkbox("selections", message="Seleccione las tareas que desea eliminar", choices=todo_choices),
        inquirer.Confirm("confirmation", message="¿Está seguro que desea eliminar estas tareas?")
    ])

    if answers["confirmation"]:
        # Update the "TODO" dictionary with updated keys
        json_object[usuario]["TODO"] = {str(int(k) - sum(1 for key in answers["selections"] if int(key) < int(k))): v
                                  for k, v in json_object[usuario]["TODO"].items() if k not in answers["selections"]}


        saveJSON()
        console.print("[bold green]Las tareas han sido eliminadas con éxito[/bold green]\nPresione cualquier tecla para continuar . . .")
    else:
        console.print("[bold red]No se eliminaron las tareas[/bold red]\nPresione cualquier tecla para continuar . . .")

    input()

def marcarTareas(usuario):
  clearScreen()
  printRule("Marcar Tareas")
  answers = inquirer.prompt([ inquirer.Checkbox("marcados", message="Seleccione las tareas completadas",
                                                choices= [(f"{index}. {json_object[usuario]["TODO"][index]["nombre"]}", index) for index in json_object[usuario]["TODO"]],
                                                default= [index for index in json_object[usuario]["TODO"] if json_object[usuario]["TODO"][index]["status"] != "\u274c"] )
                                                ])
  for index in json_object[usuario]["TODO"]:
    json_object[usuario]["TODO"][index]["status"] = "✅" if index in answers["marcados"] else "❌"
  saveJSON()
  console.print("[bold green]Se han hecho los cambios[/bold green]")
  input() 

def eliminarUsuario(usuario):
  clearScreen()
  printRule("[bold red]‼️ ELIMINAR USUARIO ‼️")
  answers = inquirer.prompt([ inquirer.Password("contraseña", message="Ingrese su contraseña"),
                             inquirer.Password("confiramcion", message="Vuelva a ingresar su contraseña."),
                             inquirer.Confirm("confirmacion", message="¿Esta seguro de borrar su cuenta?\nNo hay vuelta atrás.")])
  if answers["confirmacion"]:
    del json_object[usuario]
    console.print("[bold red]Se ha eliminado al usuario con exito.[/bold red]")
    saveJSON()
    sys.exit(0)
  else:
    console.print("[bold green]Se ha cancelado la eliminación de cuenta.[/bold green]")
  
def mainMenu(usuario):
  clearScreen()
  readJSON()
  printRule(f"TODO List de {usuario}")
  listaTODO = json_object[usuario]["TODO"]
  createTable()
  if len(listaTODO) > 0:
    for i in listaTODO:
      objetoActual = listaTODO[i]
      table.add_row(str(i), objetoActual["nombre"], objetoActual["urgencia"], objetoActual["fecha"], objetoActual["status"])
  console.print(table, justify="center")
  answers = inquirer.prompt([inquirer.List("choice", message="¿Qué desea hacer?",
                                          choices=[("1. Añadir", 1),
                                                   ("2. Modificar", 2),
                                                   ("3. Remover", 3),
                                                   ("4. Marcar / Desmcarcar", 4),
                                                   ("5. Eliminar usuario", 5),
                                                   ("6. Salir", 6)])])
  choice = answers["choice"]
  if choice == 1:
    añadir(usuario)
  elif choice == 2:
    modificar(usuario)
  elif choice == 3:
    remove(usuario)
  elif choice == 4:
    marcarTareas(usuario)
  elif choice == 5:
    eliminarUsuario(usuario)
  else:
    sys.exit(0)

def inicio():
  readJSON()
  clearScreen()
  printRule("Bienvenido a TODO List")
  cuentaExiste = inquirer.prompt([inquirer.List("metodo", 
                                                message="¿Desea crear una cuenta o iniciar sesión?",
                                                choices=[("Iniciar Sesion", 1),
                                                         ("Crear cuenta", 2)])])
  clearScreen()
  printRule("Bienvenido a TODO List")
  if cuentaExiste["metodo"] == 1:
    inicioExitoso = False
    questions = [ 
      inquirer.Text("usuario", message="Ingrese su usuario"),
      inquirer.Password("contraseña", message="Ingrese su contraseña")
    ]
    while not inicioExitoso:
      answers = inquirer.prompt(questions)
      if answers["usuario"] in json_object and answers["contraseña"] == json_object[answers["usuario"]]["password"]:
        inicioExitoso = True
        console.print("[bold]Inicio de sesión exitoso.[/bold]\nPresione cualquier tecla para continuar . . .")
        input()
        while True:
          mainMenu(answers["usuario"])
      else:
        console.print("[bold red]Ese usuario o contraseña no existen[/bold red]")
  else:
    usuario = inquirer.prompt([ inquirer.Text("usuario", message="Nombre a su usuario"), ])
    questions = [
      inquirer.Password("contraseña", message="Ingrese una contraseña"),
      inquirer.Password("confirmacionContraseña", message="Ingrese nuevamente la contraseña")
    ]
    contraseñasIguales = False
    while not contraseñasIguales:
      answers = inquirer.prompt(questions)
      if answers["contraseña"] == answers["confirmacionContraseña"]:
        contraseñasIguales = True
        console.print("[bold]Usuario creado con exito[bold]\nPresione cualquier tecla para continuar . . .")
        json_object[usuario["usuario"]] = { "password": answers["contraseña"], "TODO": {} }
        saveJSON()
        input()
        inicio()
      else:
        console.print("[bold red]Las contraseñas no son iguales, intente nuevamente ❌[/bold red]")
inicio()