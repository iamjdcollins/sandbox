import logging

#Define Node Moved Signal

def save_node(sender,instance, **kwargs):
  instance.save() 
