import bpy
from multiprocessing import shared_memory
import numpy as np
import math
class ConstantUpdateOperator(bpy.types.Operator):
    bl_idname = "wm.shared_memory_updater"
    bl_label = "Shared Memory Updater"
    _timer = None
    _shm = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            try:
                # 1. Access the shared memory
                # Assuming 'BlenderData' is created by an external app
                if self._shm is None:
                    self._shm = shared_memory.SharedMemory(name="cords")
                
                # 2. Read your data (example: first 4 bytes as floats)
                # Use shm.buf[:N] to get raw bytes
                raw_coords = bytes(self._shm.buf[:168])
                coords = np.frombuffer(raw_coords, dtype=np.float32)
                print(coords)
                
               # 3. Apply to Blender objects
                for current in range(len(coords)//2):
                    cur = current*2
                    obj = bpy.data.objects.get(f"Cube.{current:03}")
                    if obj:
                        obj.location.x = coords[cur]*100-50
                        obj.location.z = -(coords[cur+1]*100-50)
                        # Tag redraw ensures the viewport refreshes immediately
                        context.area.tag_redraw() 
#                    
            except Exception as e:
                print(f"Update error: {e}")
                return self.cancel(context)

        # Allow stopping with the ESC key
        if event.type in {'ESC'}:
            return self.cancel(context)

        return {'PASS_THROUGH'}

    def execute(self, context):
        # Register a timer to run every 0.01 seconds (~100 FPS)
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.01, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        # Cleanup is critical to prevent memory leaks or crashes
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        if self._shm:
            self._shm.close()
        return {'CANCELLED'}
# Register the operator
bpy.utils.register_class(ConstantUpdateOperator)

# To start: Run this line in the console or via a button
