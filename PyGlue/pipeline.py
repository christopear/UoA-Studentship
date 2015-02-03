from lxml import etree
from warnings import warn
from topological_sort import sort_topologically
import os
#import module

class Pipeline:
	def __init__(self, xml_file):
		self.xml_file = xml_file

		self.setup_tree()
		self.setup_namespace()	
		self.setup_root()

		self.parse_information_from_xml()
		self.read_in_modules()
		
		self.running_order = self.order_with_actual_modules()

	def setup_tree(self):
		self.tree = etree.parse(self.xml_file)

		return self.tree

	def setup_namespace(self):
		temp_namespace = self.tree.getroot().nsmap
		#formats it properly and assigns it to self
		self.namespace = "{" + temp_namespace[None] + "}"

		return self.namespace

	def setup_root(self):
		self.root = self.tree.getroot()
		return self.root

	# above completed		

	def order_with_actual_modules(self):
		ret_order = []
		for s in self.module_order:
			for individual_module in s:
				m = self.modules[individual_module]
				ret_order.append(m)
		return ret_order
		
	def run_pipeline(self):

		for m in self.running_order():
			m_py = m.create_module_py()
			#TODO
						


	def parse_information_from_xml(self):
		self.components = self.root.findall(self.namespace+"component")
		self.pipes = self.root.findall(self.namespace + "pipe")


		self.components_dict = self.create_component_dictionary()
		graph, self.variable_pipe_links = self.create_graphs()		
		self.module_order = sort_topologically(graph)
		self.module_order.reverse()

		# NOTE ON VARIABLE_PIPE_LINKS
		# IT IS 'OUTPUT' POINTING TO 'INPUT'
			
	
	def read_in_modules(self):
		self.modules = {}
		for c in self.components:
			if c.get('type') == 'module':
				module_file_name = c.get('ref')
				self.modules[module_file_name] = Module(module_file_name)

	def create_component_dictionary(self):
		# creates a dictionary
		# really simply, just maps m1 to module1.xml
		ret_dict = dict()
		for component in self.components:
			if component.get('type') == "module":
				key = component.get('name')
				reference = component.get('ref')
			
				ret_dict[key] = reference
		return ret_dict

	def create_graphs(self):
		graph = dict()
		pipe_links = dict()

		for pipe in self.pipes:
			start = pipe.find(self.namespace + "start")
			end = pipe.find(self.namespace + "end")
		
			o_component = start.get("component")
			i_component = end.get("component")
			
			o_component = self.components_dict[o_component]
			i_component = self.components_dict[i_component]

			o_variable = start.get("output")
			i_variable = end.get("input")

			pipe_links[(o_component, o_variable)] = (i_component, i_variable)

			if o_component in graph:
				# append to existing array
				graph[o_component].append(i_component)
			else:
				# create a new array in this slot
				graph[o_component] = [i_component]

		return graph, pipe_links


class Module:
	def __init__(self, xml_file):
		if not os.path.isfile(xml_file):
			raise IOError("That is not a file you fucking jerk.")

		self.xml_file = xml_file

		self.setup_tree()
		self.setup_namespace()	
		self.setup_root()

		self.parse_information_from_xml()
		self.create_module_py()

	def setup_tree(self):
		self.tree = etree.parse(self.xml_file)

		return self.tree

	def setup_namespace(self):
		temp_namespace = self.tree.getroot().nsmap
		#formats it properly and assigns it to self
		self.namespace = "{" + temp_namespace[None] + "}"

		return self.namespace

	def setup_root(self):
		self.root = self.tree.getroot()
		return self.root

	def parse_information_from_xml(self):
		self.source_file = self.search_inside_tag("source","ref")
		self.platform = self.search_inside_tag("platform","name")
		
		# These are still elements tho
		self.inputs = self.root.findall(self.namespace + "input")
		self.outputs = self.root.findall(self.namespace + "output")
		
		self.input_types, self.input_names = self.create_types_and_names(self.inputs)
		self.output_types, self.output_names = self.create_types_and_names(self.outputs)

		

	def search_inside_tag(self, tag, attribute):
		return self.root.find(self.namespace + tag).get(attribute)
	
	def __str__(self):
		return etree.tostring(self.tree,pretty_print=True)

	def create_module_py(self):
		# TODO decide whether I want to "have it" or "be it"
		self.module_py = ModulePy(self.source_file,
					self.input_names, self.output_names)
		return self.module_py

	def create_types_and_names(self, elements):
		types = []
		names = []
		for e in elements:
			types.append(e.get("type"))
			names.append(e.get("name"))

		return types, names


	def incoming_pipe(self, other):
		pass
		#TODO
	def outgoing_pipe(self, other):
		pass
		# TODO

		#('plot', 'df'): ('start', 'df')

class ModulePy:
	def __init__(self, run_file,input_var_names, output_var_names):
		# python file to run
		self.run_file = run_file

		# create a small list of the incoming and outgoing variables
		# TODO: write these as a dictionary???
		self.input_variable_names = input_var_names
		self.output_variable_names = output_var_names

		#self.run_file(run_file, other_dict) # saves to self.save_vars

	def run_file(self, run_file, other_dict):
		# get in the 'input' variables from pipes!
		pre_locals = self.filter_inputs(other_dict,self.input_variable_names)
		
		# combine them locals!
		for key in pre_locals:
			locals()[key] = pre_locals[key]

		# run the file!
		execfile(run_file)
	
		self.save_vars = locals()


	def filter_inputs(self, other_dict, input_variable_names):
		return { k: other_dict[k] for k in input_variable_names}


	def get_locals_dict(self):
		return self.save_vars

simple_pipe  = Pipeline("pipe.xml")
