import bs4

def to_camel_case(snake_string):
    return snake_string.title().replace("_", "")

with open("/home/lisa/work/python-powerdns/docs/build/html/interface.html") as handle:
    doc = handle.read()

parsed_doc = bs4.BeautifulSoup(doc, 'html.parser')
klasses = parsed_doc.find_all("dl", {"class": "py class"})

allowed_klasses = ["powerdns.interface.PDNSServer", "powerdns.interface.PDNSZone", "powerdns.interface.PDNSEndpoint"]

for klass in klasses:
    klass_name = klass.find("dt", {"class": "sig sig-object py"}).get("id")
    if not klass_name in allowed_klasses:
        print(f"Skipping {klass_name}")
        continue

    klass_params = klass.find("dl", {"class": "field-list simple"}).find_all("li") or []
    for param in klass_params:
        param_name = param.find("strong").text
        param_type = param.find("em").text
        param_desc = param.find("p") or params
        param_desc = param.text.split("–")[-1].strip()

    klass_methods = klass.find_all("dl", {"class": "py method"}) or []
    klass_properties = klass.find_all("dl", {"class": "py property"}) or []

    for properti in klass_properties:
        property_name = properti.find("span", {"class": "sig-name descname"}).text
        property_doc = properti.find("dd").find("p").text
        with open(f"get_{property_name}.yaml", "w") as handle:
            handle.write(f"""---
  name: get_{property_name}
  runner_type: "python-script"
  description: "{property_doc}"
  entry_point: "{property_name}.py"
  parameters:
    server_id:
      type: string
      description: "Server name to query."
      required: true
      default: localhost
""")

        property_cls = to_camel_case(f"get_{property_name}")
        with open(f"get_{property_name}.py", "w") as handle:
            handle.write(f"""from lib.base import PowerDNSClient

class {property_cls}(PowerDNSClient):
    def _run(self):
      return self.api.{property_name}
""")

    for method in klass_methods:
        method_name = method.find("dt", {"class": "sig sig-object py"}).get("id").split(".")[-1]
        method_doc = method.find("dd").find("p").text
        # retrieive proto to know if arg is required or not
        # remove the last two a href and their text to retrieive full proto of func
        method_params_val = method.find_all("em", {"class": "sig-param"})

        try:
            # if only one param, it's not li but p
            method_params = method.find("dl", {"class": "field-list simple"}).find_all("li") \
                or method.find("dd", {"class": "field-odd"}).find_all("p")
        except AttributeError:   # there is no args at all
            methods_params = []
        parameters = {
            "server_id": {
                "type": "string",
                "description": "Server name to query.",
                "required": True,
                "default": "localhost"
            }
        }
        if klass_name == "powerdns.interface.PDNSZone":
            parameters["zone_name"] = {
                "type": "string",
                "description": "Zone's canonical name to get details.",
                "required": True,
            }
        for params in method_params:
            param_name = params.find("strong").text
            param_type = params.find("em").text
            param_desc = params.find("p") or params
            param_desc = params.text.split("–")[-1].strip()
            param_required = True
            for item in method_params_val:
                if item.find("span", {"class": "n"}).text == param_name:
                    if item.find("span", {"class": "o"}):
                        param_required = False

                        parameters[param_name] = {
                "type": param_type,
                "description":  param_desc,
                "required": param_required
            }
        yaml_content = f"""---
  name: {method_name}
  runner_type: "python-script"
  description: "{method_doc}"
  entry_point: "{method_name}.py"
  parameters:
    server_id:
      type: string
      description: "Server name to query."
      required: true
      default: localhost
"""
        if klass_name == "powerdns.interface.PDNSZone":
            yaml_content += """    zone_name:
      type: string
      description: "Zone's canonical name to get details."
      required: true
"""
        for name, param in parameters.items():
            if name == "server_id" or name == "zone_name":
                continue
            yaml_content += f"""    {name}:
      type: {param['type']}
      description: {param['description']}
      required: {param['required']}
"""
        method_cls = to_camel_case(f"{method_name}")        
        python_content = f"""from lib.base import PowerDNSClient


class {method_cls}(PowerDNSClient):
  def _run(self, *args, **kwargs):
    return self.api.{method_name}(*args, **kwargs)
"""
        with open(f"{method_name}.yaml", "w") as handle:
            handle.write(yaml_content)

        with open(f"{method_name}.py", "w") as handle:
            handle.write(python_content)
    
