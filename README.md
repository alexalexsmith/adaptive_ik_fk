# adaptive_ik_fk

### Still in early testing so expect breaking. Automatically matches IK and FK controls as you move them while maintaining the set interpolation method. This allows you to pose in IK or Fk at the same time

## place in your scripts folder and run with below command

```from adaptive_ik_fk import adaptive_ik_fk_tool;adaptive_ik_fk_tool.run()```

## How it works
### It uses a selection changed callback to check the current selection. when an IK or FK control is selected it applies an attribute changed callback to the control. as you move the control it will match the the IK or FK controls. The UI stores and manages the callbacks
