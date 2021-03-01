from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter.font
import PIL.Image
import PIL.ImageTk
import requests
from datetime import datetime
import json
import time
from io import BytesIO
import threading
import os
import xlsxwriter
import sqlite3

raiz = Tk()
raiz.title('Instagram Following Manager')
raiz.geometry('492x590+20+20')
raiz.resizable(False, False)

def Centrar():
	raiz.update_idletasks()
	width = raiz.winfo_width()
	frm_width = raiz.winfo_rootx() - raiz.winfo_x()
	win_width = width + 2 * frm_width
	height = raiz.winfo_height()
	titlebar_height = raiz.winfo_rooty() - raiz.winfo_y()
	win_height = height + titlebar_height + frm_width
	x = raiz.winfo_screenwidth() // 2 - win_width // 2
	y = raiz.winfo_screenheight() // 2 - win_height // 2
	raiz.geometry('492x590+{}+{}'.format(x-300,y))
	

Centrar()

class EntryWithPlaceholder(Entry):
	def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', show = None ,**kw):
		super().__init__(master, kw)
		self.show = show
		self.placeholder = placeholder
		self.placeholder_color = color
		self.default_fg_color = self['fg']

		self.bind("<FocusIn>", self.foc_in)
		self.bind("<FocusOut>", self.foc_out)

		self.put_placeholder()

	def put_placeholder(self):
		self.insert(0, self.placeholder)
		self['fg'] = self.placeholder_color

	def foc_in(self, *args):
		self.config(show = self.show)
		if self['fg'] == self.placeholder_color:
			self.delete('0', 'end')
			self['fg'] = self.default_fg_color

	def foc_out(self, *args):
		if not self.get():
			self.put_placeholder()

class Instagram():
	def __init__(self, hotmail = None, password = None, cookies = None, token = None):
		self.time = int(datetime.now().timestamp())
		self.hotmail = hotmail
		self.password = password
		self.Control = {'Seguidos' : ('3dec7e2c57367ef3da3d987d89f9dbc8', 'edge_follow', 'following'), 'Seguidores' : ('5aefa9893005572d237da5068082d8d5', 'edge_followed_by', 'followers')}

		if cookies and token:
			self.cookies = cookies
			self.token = token
		else:
			self.Data_Usuario = self.Login()

			if isinstance(self.Data_Usuario, dict):
				self.token = self.Data_Usuario.get('csrf_token')
				self.Data_Usuario = self.Data_Usuario.get('viewer')

	def Cookies_Main(self):
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Language': 'es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3',
			'Referer': 'https://www.instagram.com/accounts/onetap/?next=%2F',
			'Connection': 'keep-alive',
			'Upgrade-Insecure-Requests': '1',
			'Cache-Control': 'max-age=0',
			'TE': 'Trailers',
		}

		response = requests.get('https://www.instagram.com/', headers=headers)
		return response.cookies.get_dict(), response.text.split('{"csrf_token":"')[1].split('"')[0]

	def Login(self):
		self.cookies, self.token = self.Cookies_Main()

		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
			'Accept': '*/*',
			'Accept-Language': 'es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3',
			'X-CSRFToken': self.token,
			'X-Instagram-AJAX': '48d33fb5b4b8-hot',
			'X-IG-App-ID': '936619743392459',
			'X-IG-WWW-Claim': '0',
			'Content-Type': 'application/x-www-form-urlencoded',
			'X-Requested-With': 'XMLHttpRequest',
			'Origin': 'https://www.instagram.com',
			'Connection': 'keep-alive',
			'Referer': 'https://www.instagram.com/',
			'TE': 'Trailers',
		}

		data = {
		  'username': self.hotmail,
		  'enc_password': '#PWD_INSTAGRAM_BROWSER:0:{}:{}'.format(self.time, self.password),
		  'queryParams': '{}',
		  'optIntoOneTap': 'false'
		}

		response = requests.post('https://www.instagram.com/accounts/login/ajax/', headers=headers, cookies=self.cookies, data=data)
		Estado = json.loads(response.text)

		if Estado['status'] == 'ok' and Estado['user'] == False:
			return 'Usuario inexistente'

		elif Estado['status'] == 'ok' and Estado['authenticated'] == False:
			return 'Contraseña incorrecta'	

		elif Estado['status'] == 'fail':
			return 'error'


		self.UserID = json.loads(response.text)['userId']
		cookies = response.cookies.get_dict()
		self.cookies['csrftoken'] = cookies['csrftoken']
		self.cookies['ds_user_id'] = cookies['ds_user_id']
		self.cookies['rur'] = cookies['rur']
		self.cookies['sessionid'] = cookies['sessionid']
		return self.Cookies_Login()

	def Cookies_Login(self):
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Language': 'es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3',
			'Connection': 'keep-alive',
			'Referer': 'https://www.instagram.com/accounts/login/',
			'Upgrade-Insecure-Requests': '1',
			'TE': 'Trailers',
		}

		params = (
			('next', '/'),
		)

		response = requests.get('https://www.instagram.com/accounts/onetap/', headers=headers, params=params, cookies=self.cookies)
		cookies = response.cookies.get_dict()

		try:
			self.cookies['shbid'] = cookies['shbid']
			self.cookies['shbts'] = cookies['shbts']
		except:
			pass

		return json.loads('{"config":' + response.text.split('{"config":')[1].split(';</script>')[0]).get('config')

	def Logout(self):
		headers = {
	    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
	    'Accept': '*/*',
	    'Accept-Language': 'es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3',
	    'X-CSRFToken': self.token,
	    'X-Instagram-AJAX': '0edc1000e5e7',
	    'X-IG-App-ID': '936619743392459',
	    'X-IG-WWW-Claim': 'hmac.AR3K2WqB10Nrw45bbIw62aRqQbvHckPJtge1T9UAiN5vbEDJ',
	    'Content-Type': 'application/x-www-form-urlencoded',
	    'X-Requested-With': 'XMLHttpRequest',
	    'Origin': 'https://www.instagram.com',
	    'Connection': 'keep-alive',
	    'Referer': 'https://www.instagram.com/',
	    'TE': 'Trailers',
		}

		data = {
		  'one_tap_app_login': '0',
		  'user_id': self.Data_Usuario['id']
		}
		response = requests.post('https://www.instagram.com/accounts/logout/ajax/', headers=headers, cookies=self.cookies, data=data)

		if json.loads(response.text)['status'] == 'ok':
			return True


	def InfoUsuarios(self, usuario):
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
			'Accept': '*/*',
			'Accept-Language': 'es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3',
			'X-IG-App-ID': '936619743392459',
			'X-IG-WWW-Claim': 'hmac.AR3K2WqB10Nrw45bbIw62aRqQbvHckPJtge1T9UAiN5vbOWo',
			'X-Requested-With': 'XMLHttpRequest',
			'Connection': 'keep-alive',
			'Referer': 'https://www.instagram.com/camipanne/',
			'TE': 'Trailers',
		}

		params = (
			('__a', '1'),
		)

		response = requests.get('https://www.instagram.com/{}/'.format(usuario), headers=headers, params=params, cookies=self.cookies)
		Json_Response = json.loads(response.text)
		self.Data = {}

		if Json_Response == {}:
			return False

		Info = Json_Response.get('graphql').get('user')

		self.Data['id'] = Info.get('id')
		self.Data['username'] = Info.get('username')
		self.Data['full_name'] = Info.get('full_name')
		self.Data['biography'] = Info.get('biography')
		self.Data['privada'] = Info.get('is_private')
		self.Data['verificada'] = Info.get('is_verified')
		self.Data['category_name'] = Info.get('category_name')
		self.Data['external_url'] = Info.get('external_url')
		self.Data['publicaciones'] = Info.get('edge_owner_to_timeline_media').get('count')
		self.Data['seguidores'] = Info.get('edge_followed_by').get('count')
		self.Data['seguidos'] = Info.get('edge_follow').get('count')
		self.Data['seguido'] = Info.get('followed_by_viewer')
		self.Data['seguidores_mutuos'] = Info.get('edge_mutual_followed_by').get('count')
		self.Data['profile_pic_url'] = Info.get('profile_pic_url')
		self.Data['profile_pic_url_hd'] = Info.get('profile_pic_url_hd')
		self.Dict_Info = {'Seguidores' : [], 'Seguidos' : []}
		self.after_token = {'Seguidores' : None, 'Seguidos' : None}
		return self.Data

	def Get_Follows(self, MaxSeguidores = 'all', hash_query = 'Seguidores'):
		if MaxSeguidores == 'all':
			MaxSeguidores = self.Data[hash_query.lower()]

		headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
		'Accept': '*/*',
		'Accept-Language': 'es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3',
		'X-CSRFToken': self.token,
		'X-IG-App-ID': '936619743392459',
		'X-IG-WWW-Claim': 'hmac.AR3K2WqB10Nrw45bbIw62aRqQbvHckPJtge1T9UAiN5vbJc9',
		'X-Requested-With': 'XMLHttpRequest',
		'Connection': 'keep-alive',
		'Referer': 'https://www.instagram.com/{}/{}/'.format(self.Data['username'], self.Control[hash_query][2]),
		'TE': 'Trailers',
		}

		if self.after_token[hash_query] == False:
			return

		elif self.after_token[hash_query]:
			params = (
				('query_hash', self.Control[hash_query][0]),
				('variables', '{"id":"%s","include_reel":true,"fetch_mutual":false,"first":12,"after":"%s"}'%(self.Data['id'], self.after_token[hash_query])),
			)

		else:
			params = (
				('query_hash', self.Control[hash_query][0]),
				('variables', '{"id":"%s","include_reel":true,"fetch_mutual":true,"first":24}'%(self.Data['id'])),
			)

		response = requests.get('https://www.instagram.com/graphql/query/', headers=headers, params=params, cookies=self.cookies)
		JsonResponse = json.loads(response.text)

		if JsonResponse['status'] == 'fail' and JsonResponse['message'] == 'rate limited':
			return 'rate limited'

		for usuarios in JsonResponse.get('data').get('user').get(self.Control[hash_query][1]).get('edges'):
			if MaxSeguidores != 'all' and MaxSeguidores <= len(self.Dict_Info[hash_query]):
				return round(len(self.Dict_Info[hash_query])/MaxSeguidores*100), self.Dict_Info[hash_query]

			Info_Seguidor = usuarios.get('node')
			del Info_Seguidor['reel']
			self.Dict_Info[hash_query].append(Info_Seguidor)


		try:
			self.after_token[hash_query] = JsonResponse.get('data').get('user').get(self.Control[hash_query][1]).get('page_info').get('end_cursor')
			return round(len(self.Dict_Info[hash_query])/MaxSeguidores*100), self.Dict_Info[hash_query]
		except:
			pass

class Backend():
	def AcortarNumero(self, numero):
		numero = str(numero)
		Largo_Numero = len(numero)
		if Largo_Numero == 4:
			return numero[0] + '.' + numero[1:]
		elif Largo_Numero == 5:
			return numero[0:2] + '.' + numero[2:]
		elif Largo_Numero == 6:
			return numero[0:3] + '.' + numero[3] + 'k'
		elif Largo_Numero == 7:
			return numero[0] + '.' + numero[1] + 'mm'
		elif Largo_Numero == 8:
			return numero[0:2] + '.' + numero[2] + 'mm'
		elif Largo_Numero == 9:
			return numero[0:3] + '.' + numero[3] + 'mm'
		else:
			return numero

	def Login(self):
		self.Sesion_Activa.config(state = 'disabled')
		if self.Logueado:
			self.Label_Barra.config(text = 'Logger: Cerrando sesión')
			self.Boton_Lupa.config(state = 'disabled')
			self.Boton_Comenzar.config(state = 'disabled')
			if self.Sesion.Logout():
				self.Name.place_forget()
				self.Full_Name.place_forget()
				self.Portada.config(image = self.Imagenes['Inicio_Sesion'])
				self.Sesion_Activa.config(image = self.Imagenes['Boton_Sesion'])
				self.Hotmail.place(x=170,y=25, width=308)
				self.Contraseña.place(x=170,y=65, width=308)
				self.Cuenta_Privada.config(image = self.Imagenes['Candado_Abierto'])
				self.Label_Barra.config(text = 'Logger: Sesión cerrada correctamente')
				self.Logueado = False
			else:
				self.Label_Barra.config(text = 'Logger: Hubo un problema al cerrar sesión')

		else:
			self.Label_Barra.config(text = 'Logger: Iniciando sesión')
			self.Sesion = Instagram(self.String_Hotmail.get(), self.String_Contraseña.get())

			if self.Sesion.Data_Usuario == 'Usuario inexistente':
				self.Label_Barra.config(text = 'Logger: Usuario inexistente')
			elif self.Sesion.Data_Usuario == 'Contraseña incorrecta':
				self.Label_Barra.config(text = 'Logger: Contraseña incorrecta')
			elif self.Sesion.Data_Usuario == 'error':
				self.Label_Barra.config(text = 'Logger: Error al iniciar sesión')
			else:
				self.Hotmail.place_forget()
				self.Contraseña.place_forget()
				self.Name.config(text = 'Username: ' + self.Sesion.Data_Usuario['username'])
				self.Name.place(x = 170, y = 15, width = 310)
				self.Full_Name.config(text = 'Full Name: ' + self.Sesion.Data_Usuario['full_name'])
				self.Full_Name.place(x = 170, y = 48, width = 310)
				self.Portada.config(image = self.CargarImagen(self.Sesion.Data_Usuario['profile_pic_url_hd'], (140, 140)))
				self.Sesion_Activa.config(image = self.Imagenes['Cerrar_Sesion'])

				if self.Sesion.Data_Usuario['is_private']:
					self.Cuenta_Privada.config(image = self.Imagenes['Candado_Cerrado'])
				else:
					self.Cuenta_Privada.config(image = self.Imagenes['Candado_Abierto'])
				self.Logueado = True
				self.Label_Barra.config(text = 'Logger: Sesión iniciada')
				self.Boton_Lupa.config(state = 'normal')

		self.Sesion_Activa.config(state = 'normal')

	def Buscar_Usuario(self):
		self.Label_Barra.config(text = 'Logger: Buscando usuario')
		self.Sesion_Activa.config(state = 'disabled')
		self.Boton_Comenzar.config(state = 'disabled')
		self.Boton_Lupa.config(state = 'disabled')
		self.Data = self.Sesion.InfoUsuarios(self.String_Buscar.get())
		
		if self.Data:
			self.Label_Barra.config(text = 'Logger: Usuario encontrado')
			self.String_buscado_name.set(self.Data['full_name'])
			self.buscado_publicaciones.config(text = 'Publicaciones\n' + self.AcortarNumero(self.Data['publicaciones']))
			self.buscado_seguidores.config( text = 'Seguidores\n' + self.AcortarNumero(self.Data['seguidores']))
			self.buscado_seguidos.config(text = 'Seguidos\n' + self.AcortarNumero(self.Data['seguidos']))
			self.buscado_Portada.config(image = self.CargarImagen(self.Data['profile_pic_url_hd'], (140, 140)))

			if self.Data['privada']:
				self.buscado_privado.config(image = self.Imagenes['Candado_Cerrado'])
			else:
				self.buscado_privado.config(image = self.Imagenes['Candado_Abierto'])

			if self.Data['verificada']:
				self.buscado_famoso.place_slaves()
			else:
				self.buscado_famoso.place_forget()

			if self.Data['seguido']:
				self.buscado_siguiendo.config(text = 'Siguiendo: Si')
			else:
				self.buscado_siguiendo.config(text = 'Siguiendo: No')
			self.Boton_Comenzar.config(state = 'normal')
		else:
			self.Label_Barra.config(text = 'Logger: El usuario no existe')

		self.Sesion_Activa.config(state = 'normal')
		self.Boton_Comenzar.config(state = 'normal')
		self.Boton_Lupa.config(state = 'disabled')

	def Comenzar_Proceso(self):
		self.Boton_Lupa.config(state = 'disabled')
		self.Boton_Comenzar.config(state = 'disabled')
		self.Sesion_Activa.config(state = 'disabled')
		self.Check_Seguidores.config(state = 'disabled')
		self.Check_Seguidos.config(state = 'disabled')
		self.Check_Pagina.config(state = 'disabled')
		self.Check_Excel.config(state = 'disabled')
		self.Check_Json.config(state = 'disabled')
		self.Check_Sql.config(state = 'disabled')

		TCheck_Seguidores = self.Check_Seguidores_Int.get()
		TCheck_Seguidos = self.Check_Seguidos_Int.get()
		Conseguir_Seguidores = True
		Conseguir_Seguidos = True
		TCheck_Pagina = self.Check_Pagina_Int.get()
		TCheck_Excel = self.Check_Excel_Int.get()
		TCheck_Json = self.Check_Json_Int.get()
		TCheck_Sql = self.Check_Sql_Int.get()

		if TCheck_Pagina == False and TCheck_Excel == False and TCheck_Json == False and TCheck_Sql == False:
			self.Label_Barra.config(text = 'Logger: Seleccine almenos un metodo de guardado')
			return

		if TCheck_Seguidores == False and TCheck_Seguidos == False:
			self.Label_Barra.config(text = 'Logger: Seleccine seguidores/seguidos')
			return

		Seguidores = '  '
		Seguidos = '  '
		Max_Seguidores = self.Max_Seguidores.get()
		Max_Seguidos = self.Max_Seguidos.get()

		if Max_Seguidores.isdigit():
			Max_Seguidores = int(Max_Seguidores)
		else:
			Max_Seguidores = 'all'

		if Max_Seguidos.isdigit():
			Max_Seguidos = int(Max_Seguidos)
		else:
			Max_Seguidos = 'all'

		if TCheck_Seguidores:
			while Seguidores[0] != 100:
				Seguidores = self.Sesion.Get_Follows(MaxSeguidores=Max_Seguidores, hash_query='Seguidores')
				
				if Seguidores == 'rate limited':
					self.Label_Barra.config(text = 'Logger: ')
					Seguidores = self.Dict_Info['Seguidores']
					if messagebox.askquestion('Error', 'Has lledo al limite de solicitudes\n¿Quiere guardar los {} seguidores conseguidos?'.format(len(Seguidores[1]))) == 'no':
						Conseguir_Seguidores = False
						Seguidores = None
					break

				self.Barra_Variable.set(Seguidores[0])
				self.Label_Barra.config(text = 'Logger: Consiguiendo seguidores; {}%'.format(str(Seguidores[0])))

		if TCheck_Seguidos:
			while Seguidos[0] != 100:
				Seguidos = self.Sesion.Get_Follows(MaxSeguidores=Max_Seguidos, hash_query='Seguidos')

				if Seguidos == 'rate limited':
					self.Label_Barra.config(text = 'Logger: ')
					Seguidos = self.Dict_Info['Seguidos']
					if messagebox.askquestion('Error', 'Has lledo al limite de solicitudes\n¿Quiere guardar los {} seguidos conseguidos?'.format(len(Seguidores[1]))) == 'no':
						Conseguir_Seguidos = False
						Seguidos = None
					break

				self.Barra_Variable.set(Seguidos[0])
				self.Label_Barra.config(text = 'Logger: Consiguiendo seguidos; {}%'.format(str(Seguidos[0])))
		self.Barra_Variable.set(0)

		Dict_Info = {'Seguidores' : Seguidores[1], 'Seguidos' : Seguidos[1]}
		Ruta_Guardar = 'Guardado/{}/{}'.format(self.Data['username'], time.strftime("%Y-%m-%d-%H;%M"))
		if os.path.exists(Ruta_Guardar):
			Ruta_Guardar = 'Guardado/{}/{}'.format(self.Data['username'], time.strftime("%Y-%m-%d-%H;%M;%S"))
			os.makedirs(Ruta_Guardar)
		else:
			os.makedirs(Ruta_Guardar)

		Info_Seg = []
		if TCheck_Seguidores and Conseguir_Seguidores:
			Info_Seg.append('Seguidores')
		if TCheck_Seguidos and Conseguir_Seguidos:
			Info_Seg.append('Seguidos')

		if TCheck_Pagina:
			self.Label_Barra.config(text = 'Logger: Creando página web')
			os.makedirs(Ruta_Guardar + '/Html/')

			for x in Info_Seg:
				Html = """<!DOCTYPE HTML>
				<html>
					<head>
						<title>Instagram Data</title>
						<link rel="stylesheet" href="styles.css"/>
					</head>

					<body>"""

				for Info in Dict_Info[x]:
					Html+="""
						<figure>
							<img src="{}">
							<p>Id: <strong>{}</strong></p>
							<p>User: <strong>{}</strong></p>
							<p>Name: <strong>{}</strong></p>
						</figure>
				""".format(Info['profile_pic_url'], Info['id'], Info['username'], Info['full_name'])

				Html+="""
					</body>
				</html>
				"""

				Css = """body{
							background-color: #CCC;
						}


						figure{
							float:left;
							height: 300px;
							padding-right: 50px;
							padding-left: 50px;
							margin-left: auto;
							margin-right: auto;
						   }
						   
						#contenedor{
							width:91%;
							margin: 15px auto;
							/*margin-left: auto;
							margin-right: auto;*/
						}

						figure img{
							width: 190px;
							height: 190px;
							padding:4px;
							background:#666;
							border-radius:20px;
							transition:transform 0.3s ease-in-out 0.1s;
						   }

						p{
							font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
							font-size: 16px;
							margin-top:5px;
							margin: 2px;
							max-width: 200px;
						   }"""

				with open(Ruta_Guardar + '/Html/%s.html'%(x), 'w', encoding="utf-8") as fp:
					fp.write(Html)

			with open(Ruta_Guardar + '/Html/styles.css', 'w', encoding="utf-8") as fp:
				fp.write(Css)

		if TCheck_Excel:
			self.Label_Barra.config(text = 'Logger: Creando éxcel')
			workbook = xlsxwriter.Workbook(Ruta_Guardar + '/Excel.xlsx')
			Format = workbook.add_format()
			Format.set_bg_color('#F88484')
			Format.set_align('center')

			for Nombre in Info_Seg:
				worksheet = workbook.add_worksheet(Nombre)
				worksheet.set_column(0, 0, 17)
				worksheet.set_column(1, 2, 27)
				worksheet.set_column(3, 3, 22)
				worksheet.set_column(4, 8, 23)
				worksheet.write('A1', 'id', Format) 
				worksheet.write('B1', 'username', Format) 
				worksheet.write('C1', 'full_name', Format) 
				worksheet.write('D1', 'profile_pic_url', Format)
				worksheet.write('E1', 'is_private', Format)
				worksheet.write('F1', 'is_verified', Format)
				worksheet.write('G1', 'followed_by_viewer', Format)
				worksheet.write('H1', 'follows_viewer', Format)
				worksheet.write('I1', 'requested_by_viewer', Format)

				for C, Info in enumerate(Dict_Info[Nombre]):
					Numero = C+2
					worksheet.write('A%d'%(Numero), Info['id'])
					worksheet.write('B%d'%(Numero), Info['username'])
					worksheet.write('C%d'%(Numero), Info['full_name'])
					worksheet.write('D%d'%(Numero), Info['profile_pic_url'])
					worksheet.write('E%d'%(Numero), Info['is_private'])
					worksheet.write('F%d'%(Numero), Info['is_verified'])
					worksheet.write('G%d'%(Numero), Info['followed_by_viewer'])
					worksheet.write('H%d'%(Numero), Info['follows_viewer'])
					worksheet.write('I%d'%(Numero), Info['requested_by_viewer'])
			workbook.close()

		if TCheck_Json:
			self.Label_Barra.config(text = 'Logger: Creando json')
			with open(Ruta_Guardar + '/Json.json', 'w') as fp:
				json.dump(Dict_Info, fp, indent = 4)
		
		if TCheck_Sql:
			self.Label_Barra.config(text = 'Logger: Creando sql')
			conn = sqlite3.connect(Ruta_Guardar + '/Sql.sql')
			cursor = conn.cursor()

			for Nombre in Info_Seg:

				cursor.execute('''
				CREATE TABLE {}(
				id text,
				username text,
				full_name text,
				profile_pic_url text,
				is_private text,
				is_verified text,
				followed_by_viewer text,
				follows_viewer text,
				requested_by_viewer text)'''.format(Nombre))

				for Info in Dict_Info[Nombre]:
					cursor.execute("""INSERT INTO {} (id, username, full_name, profile_pic_url, is_private, is_verified, followed_by_viewer, follows_viewer, requested_by_viewer) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""".format(Nombre), (Info['id'], Info['username'], Info['full_name'], Info['profile_pic_url'], Info['is_private'], Info['is_verified'], Info['followed_by_viewer'], Info['follows_viewer'], Info['requested_by_viewer']))

			conn.commit()
			conn.close()

		self.Boton_Lupa.config(state = 'normal')
		self.Boton_Comenzar.config(state = 'normal')
		self.Sesion_Activa.config(state = 'normal')
		self.Check_Seguidores.config(state = 'normal')
		self.Check_Seguidos.config(state = 'normal')
		self.Check_Pagina.config(state = 'normal')
		self.Check_Excel.config(state = 'normal')
		self.Check_Json.config(state = 'normal')
		self.Check_Sql.config(state = 'normal')

		self.Label_Barra.config(text = 'Logger: Toda la información fue guardada correctamente')

	def CerrarTkinter(self):
		if self.Logueado == True and messagebox.askquestion('Cerrar', '¿Queres cerrar sesión antes de salir? de no hacerlo, la sesión quedara activa') == 'yes':
			self.Login()
		raiz.destroy()


class Fronted(Backend):
	def __init__(self):
		raiz.protocol("WM_DELETE_WINDOW", self.CerrarTkinter)
		self.Logueado = False
		self.Imagenes = {'fondo' : self.CargarImagen('Img/fondo.png', (500, 600)), 'Inicio_Sesion' : self.CargarImagen('Img/InicioSesion.jpg', (140,140)), 'Boton_Sesion' : self.CargarImagen('Img/Boton_Sesion.png', (304,45)), 'Lupa' : self.CargarImagen('Img/Lupa_Buscar.png', (26,26)), 'Verificado' : self.CargarImagen('Img/Verificado.png', (24, 24)), 'Candado_Abierto' : self.CargarImagen('Img/Candado_Abierto.png', (18, 24)), 'Candado_Cerrado' : self.CargarImagen('Img/Candado_Cerrado.png', (18, 24)), 'Cerrar_Sesion' : self.CargarImagen('Img/Boton_Cerrar_Sesion.png', (304, 45))}
		self.CargarWidgets()

	def CargarWidgets(self):
		Label(raiz, image = self.Imagenes['fondo']).pack()

		Segoe_UI15 = tkinter.font.Font( family = "Segoe UI",  size = 15,  weight = "bold") 
		Segoe_UI13 = tkinter.font.Font( family = "Segoe UI",  size = 13,  weight = "bold") 
		Segoe_UI11 = tkinter.font.Font( family = "Segoe UI",  size = 11,  weight = "bold") 

		self.String_Hotmail = StringVar()
		self.String_Contraseña = StringVar()

		self.Portada = Label(raiz, image = self.Imagenes['Inicio_Sesion'])
		self.Portada.place(x=11,y=15)
		self.Hotmail = EntryWithPlaceholder(raiz, "Teléfono, usuario o correo electrónico", textvariable = self.String_Hotmail, font = Segoe_UI15)
		self.Hotmail.place(x=170,y=25, width=310)
		self.Contraseña = EntryWithPlaceholder(raiz, "Contraseña", textvariable = self.String_Contraseña, font = Segoe_UI15, show = '*')
		self.Contraseña.place(x=170,y=65, width=310)
		self.Sesion_Activa = Button(raiz, image = self.Imagenes['Boton_Sesion'], command = lambda: threading.Thread(target=self.Login).start() , relief='flat')
		self.Sesion_Activa.place(x=170,y=108)
		self.Name = Label(raiz, text = '', font = Segoe_UI11)
		self.Full_Name = Label(raiz, text = '', font = Segoe_UI11)
		self.Cuenta_Privada = Label(self.Portada, image = self.Imagenes['Candado_Abierto'], relief='flat')
		self.Cuenta_Privada.place(x = 116,y = 111)

		Canvas_Line = Frame(raiz, width=500, height=3, bg="#CCC").place(x=0,y=176)

		self.String_Buscar = StringVar()
		Buscar_Usuario = EntryWithPlaceholder(raiz, "Buscar usuario", textvariable = self.String_Buscar, font = Segoe_UI15).place(x=11,y=195, width=432)
		self.Boton_Lupa = Button(raiz, state = 'disabled', image = self.Imagenes['Lupa'], relief='flat', command = lambda: threading.Thread(target=self.Buscar_Usuario).start())
		self.Boton_Lupa.place(x=448,y=195)

		self.String_buscado_name = StringVar()

		self.buscado_Portada = Label(raiz, image = self.Imagenes['Inicio_Sesion'])
		self.buscado_Portada.place(x = 11,y = 258)
		Frame_FamaYPrivado = Frame(raiz, width = 144, height = 26)
		Frame_FamaYPrivado.place(x = 11, y = 410)
		self.buscado_famoso = Label(Frame_FamaYPrivado, image = self.Imagenes['Verificado'])
		self.buscado_famoso.place(x = 84, y = -1)
		self.buscado_privado = Label(Frame_FamaYPrivado, image = self.Imagenes['Candado_Cerrado'])
		self.buscado_privado.place(x = 115, y = -1)
		buscado_name = Entry(raiz, textvariable = self.String_buscado_name, font = Segoe_UI11, state='readonly').place(x = 11, y = 440, width = 144)
		self.buscado_siguiendo = Label(raiz, text = 'Siguiendo: No', font = Segoe_UI11, anchor="w")
		self.buscado_siguiendo.place(x= 11, y = 470, width = 144)

		self.buscado_publicaciones = Label(raiz, text = 'Publicaciones\n', font = Segoe_UI13, anchor="w")
		self.buscado_publicaciones.place(x = 170, y = 258)
		self.buscado_seguidores = Label(raiz, text = 'Seguidores\n', font = Segoe_UI13, anchor="w")
		self.buscado_seguidores.place(x = 295, y = 258)
		self.buscado_seguidos = Label(raiz, text = 'Seguidos\n', font = Segoe_UI13, anchor="w")
		self.buscado_seguidos.place(x = 397, y = 258, width = 83)

		style = ttk.Style()
		style.configure("BW.TCheckbutton",font=Segoe_UI13)

		self.Check_Seguidores_Int = IntVar()
		self.Check_Seguidos_Int = IntVar()
		self.Check_Pagina_Int = IntVar()
		self.Check_Excel_Int = IntVar()
		self.Check_Json_Int = IntVar()
		self.Check_Sql_Int = IntVar()
		self.Max_Seguidores = StringVar()
		self.Max_Seguidos = StringVar()

		FrameGuardar = Frame(raiz, width = 310, height = 161)
		FrameGuardar.place(x = 170, y =  335)

		self.Check_Seguidores = ttk.Checkbutton(FrameGuardar, variable = self.Check_Seguidores_Int, text = 'Seguidores', style="BW.TCheckbutton")
		self.Check_Seguidores.place(x = 8, y = 10)
		self.Check_Seguidos = ttk.Checkbutton(FrameGuardar, variable = self.Check_Seguidos_Int, text = 'Seguidos', style="BW.TCheckbutton")
		self.Check_Seguidos.place(x = 8, y = 35)
		EntryWithPlaceholder(FrameGuardar, 'Max Seguidores', textvariable = self.Max_Seguidores).place(x = 8, y = 68, width = 140)
		EntryWithPlaceholder(FrameGuardar, 'Max Seguidos', textvariable = self.Max_Seguidos).place(x = 8, y = 92, width = 140)

		self.Check_Pagina = ttk.Checkbutton(FrameGuardar, variable = self.Check_Pagina_Int, text = 'Página', style="BW.TCheckbutton")
		self.Check_Pagina.place(x = 205, y = 10)
		self.Check_Excel = ttk.Checkbutton(FrameGuardar, variable = self.Check_Excel_Int, text = 'Excel', style="BW.TCheckbutton")
		self.Check_Excel.place(x = 205, y = 35)
		self.Check_Json = ttk.Checkbutton(FrameGuardar, variable = self.Check_Json_Int, text = 'JSON', style="BW.TCheckbutton")
		self.Check_Json.place(x = 205, y = 60)
		self.Check_Sql = ttk.Checkbutton(FrameGuardar, variable = self.Check_Sql_Int, text = 'SQL', style="BW.TCheckbutton")
		self.Check_Sql.place(x = 205, y =  85)

		self.Boton_Comenzar = Button(FrameGuardar, state = 'disabled', text = 'Comenzar', font = Segoe_UI13, bg='#CCC', command =  lambda: threading.Thread(target=self.Comenzar_Proceso).start())
		self.Boton_Comenzar.place(x = 5, y = 118, width = 298)

		self.Barra_Variable = IntVar()
		self.Barra_Carga = ttk.Progressbar(raiz, variable = self.Barra_Variable).place(x = 11, y = 520, width = 469)
		self.Label_Barra = Label(raiz, font = Segoe_UI11, text='Logger: ')
		self.Label_Barra.place(x=11, y = 550, width = 469)

	def CargarImagen(self, Ruta, Medidas):
		if Ruta.startswith('http'):
			response = requests.get(Ruta)
			Ruta = response.content
			Ruta = BytesIO(Ruta)

		pil_image = PIL.Image.open(Ruta)
		pil_image = pil_image.resize((Medidas[0],Medidas[1]))
		tk_image = PIL.ImageTk.PhotoImage(pil_image)
		label = Label(image=tk_image)
		label.image = tk_image
		return tk_image





Fronted()
raiz.mainloop()