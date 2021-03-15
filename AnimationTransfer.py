import pymel.core as pm
import pymel.core.datatypes as dt

sourcelist = []
targetlist = []
winTitle = ""
winWidth = 500
winHeight = 400
sroot = ""
troot = ""
orientations = {}
bindPoses = {}
parents = {}
parentMatrices = {}

def RefreshUI():
    global sroot
    global troot
    sroot = cmds.textField("sourceroot", tx=True, q=True)
    troot = cmds.textField("targetroot", tx=True, q=True)
    
    print(sroot)
    
    sroot = pm.ls(sroot)
    troot = pm.ls(troot)
    
    print(sroot)
    
    cmds.textScrollList(sourcelist, e=True, removeAll=True)
    cmds.textScrollList(targetlist, e=True, removeAll=True)
    
    if len(sroot) > 0:
        hierarcy = pm.listRelatives(sroot, allDescendents=True, type='joint') + sroot
        hierarcy.reverse()
        for joint in hierarcy:
            cmds.textScrollList(sourcelist, e=True, append=str(joint))
        cmds.textScrollList(sourcelist, e=True, sii=1)
    
    if len(troot) > 0:
        hierarcy = pm.listRelatives(troot, allDescendents=True, type='joint') + troot
        hierarcy.reverse()
        for joint in hierarcy:
            cmds.textScrollList(targetlist, e=True, append=str(joint))
        cmds.textScrollList(targetlist, e=True, sii=1)

def RemoveSelected(list):
    selected = cmds.textScrollList(list, q=True, si=1)
    if selected != "":
        cmds.textScrollList(list, e=True, ri=selected)
        
def MoveUp(list):
    selectedIndex = cmds.textScrollList(list, q=True, sii=1)[0]
    if selectedIndex != 1:
        newIndex = selectedIndex - 1
        selected = cmds.textScrollList(list, q=True, si=1)[0]
        cmds.textScrollList(list, e=True, dii=selectedIndex)
        cmds.textScrollList(list, e=True, sii=newIndex)
        swapval = cmds.textScrollList(list, q=True, si=1)[0]
        cmds.textScrollList(list, e=True, rii=newIndex)
        cmds.textScrollList(list, e=True, ap=(newIndex, selected))
        cmds.textScrollList(list, e=True, rii=selectedIndex)
        cmds.textScrollList(list, e=True, ap=(selectedIndex, swapval))
        cmds.textScrollList(list, e=True, sii=newIndex)
        
def MoveDown(list):
    selectedIndex = cmds.textScrollList(list, q=True, sii=1)[0]
    sizeOfList = cmds.textScrollList(list, q=True, ni=True)
    if selectedIndex != sizeOfList:
        newIndex = selectedIndex + 1
        selected = cmds.textScrollList(list, q=True, si=1)[0]
        cmds.textScrollList(list, e=True, dii=selectedIndex)
        cmds.textScrollList(list, e=True, sii=newIndex)
        swapval = cmds.textScrollList(list, q=True, si=1)[0]
        cmds.textScrollList(list, e=True, rii=newIndex)
        cmds.textScrollList(list, e=True, ap=(newIndex, selected))
        cmds.textScrollList(list, e=True, rii=selectedIndex)
        cmds.textScrollList(list, e=True, ap=(selectedIndex, swapval))
        cmds.textScrollList(list, e=True, sii=newIndex)

def Execute():
    TransferAnimation(sroot, troot)

def BuildUI():    
    global winTitle
    winTitle = "AnimationTransfer"     
    if cmds.window(winTitle, exists=True):        
        cmds.deleteUI(winTitle)  
          
    cmds.window(winTitle, width=winWidth, height=winHeight, title=winTitle, s=False)    
    mainCL = cmds.columnLayout()    
    tmpRowWidth = [winWidth / 2, winWidth / 2]    
    
    columnAttch = [(1, "left", winWidth/4 - 5), (2, "right", winWidth/4)] 
    cmds.rowLayout(numberOfColumns=2, columnWidth2=tmpRowWidth, height=40, cat=columnAttch)    
    cmds.text(label="Source Skeleton", width=winWidth/4, fn="boldLabelFont")
    cmds.text(label="Target Skeleton", width=winWidth/4, fn="boldLabelFont")       
    cmds.setParent("..")   
    
    columnAttch = [(1, "left", winWidth/4), (2, "right", winWidth/4)] 
    cmds.rowLayout(numberOfColumns=2, columnWidth2=tmpRowWidth, height=40, cat=columnAttch)    
    cmds.textField("sourceroot", tx="", width=120, tcc="RefreshUI()")
    cmds.textField("targetroot", tx="", width=120, tcc="RefreshUI()")    
    cmds.setParent("..") 

    tmpRowWidth = [winWidth / 4, winWidth / 4, winWidth / 4, winWidth / 4]
    columnAttach = [(1, "left", 35), (2, "right", 5), (3, "left", 5), (4, "left", 30)]
    cmds.rowLayout(numberOfColumns=4, columnWidth4=tmpRowWidth, height=250, cat=columnAttach)
    
    cmds.columnLayout(rs=10, cw=50, adj=True)
    cmds.button(l="Up", c="MoveUp(sourcelist)")
    cmds.button(l="Remove", c="RemoveSelected(sourcelist)")
    cmds.button(l="Down", c="MoveDown(sourcelist)")    
    cmds.setParent("..") 
    
    global sourcelist
    global targetlist
    sourcelist = cmds.textScrollList(nr=15, ams=True, width=120)
    targetlist = cmds.textScrollList(nr=15, ams=True, width=120)

    cmds.columnLayout(rs=10, cw=100, adj=True)
    cmds.button(l="Up", c="MoveUp(targetlist)")
    cmds.button(l="Remove", c="RemoveSelected(targetlist)")
    cmds.button(l="Down", c="MoveDown(targetlist)")      
    cmds.setParent("..") 
    cmds.setParent("..") 
    
    cmds.rowLayout(numberOfColumns=1, cw1=winWidth, height=60, cat=(1, "both", winWidth / 2 - 55))    
    cmds.button(l="Transfer Animation", c="Execute()")      
    
    cmds.showWindow(winTitle)    
    cmds.window(winTitle, e=True, width=winWidth, height=winHeight)

def SetConstants(sourcejoints, targetjoints):
    pm.currentTime(-1)
    for i in range(len(sourcejoints)):
        orientations[sourcejoints[i]] = sourcejoints[i].getOrientation().asMatrix()
        bindPoses[sourcejoints[i]] = sourcejoints[i].getRotation().asMatrix()
        
        orientations[targetjoints[i]] = targetjoints[i].getOrientation().asMatrix()
        bindPoses[targetjoints[i]] = targetjoints[i].getRotation().asMatrix()
        
        parents[sourcejoints[i]] = sourcejoints[i].getAllParents()
        parents[targetjoints[i]] = targetjoints[i].getAllParents()
    
    for i in range(len(sourcejoints)):
        parentMatrices[sourcejoints[i]] = GetParentMatrix(parents[sourcejoints[i]])
        parentMatrices[targetjoints[i]] = GetParentMatrix(parents[targetjoints[i]])

def GetParentMatrix(jointparents):
    parentMatrix = dt.Matrix()
    bindPose = dt.Matrix()
    orientation = dt.Matrix()
    for p in jointparents:
        if bindPoses.has_key(p):
            orientation = orientations[p]
            bindPose = bindPoses[p]
        parentMatrix = parentMatrix *(bindPose * orientation)
    return parentMatrix

def GetIsolatedRotation(joint, key):
    bp = bindPoses[joint]
    rot = joint.getRotation().asMatrix()
    isolatedRotation = bp.transpose() * rot
    return isolatedRotation

def GetWorldRotation(joint, key):
    sourceParents = parentMatrices[joint]
    isolatedRot = GetIsolatedRotation(joint, key)
    worldSpaceRot = orientations[joint].transpose() * sourceParents.transpose() * isolatedRot * sourceParents * orientations[joint]
    return worldSpaceRot

def SetRotation(sourcejoint, targetjoint, key):
    targetParents = parentMatrices[targetjoint]
    localSpaceRot = orientations[targetjoint] * targetParents * GetWorldRotation(sourcejoint, key) * targetParents.transpose() * orientations[targetjoint].transpose()
    finalRot = bindPoses[targetjoint] * localSpaceRot
    rotInDegrees = dt.degrees(dt.EulerRotation(finalRot))
    targetjoint.setRotation(rotInDegrees)
    targetjoint.rotate.setKey()

def TransferAnimation(sourceroot, targetroot):
    s_joints = pm.listRelatives(sourceroot, allDescendents=True, type='joint') + sourceroot
    s_joints.reverse()
    
    i = 0
    s_list = cmds.textScrollList(sourcelist, q=True, ai=True)
    jointNum = len(s_list)
    
    while i < len(s_joints):
        if s_list.count(s_joints[i]) == 0:
            s_joints.pop(i)
            i -= 1  
        else:
            if i < len(s_list):
                if s_list[i] == str(s_joints[i]):
                    i += 1
                    continue
                else:
                    j = i
                    while j < len(s_joints):
                        if s_list[i] == str(s_joints[j]):         
                            temp = s_joints[i]
                            s_joints[i] = s_joints[j]
                            s_joints[j] = temp
                            break
                        j += 1

    t_joints = pm.listRelatives(targetroot, allDescendents=True, type='joint') + targetroot
    t_joints.reverse()
    
    i = 0
    t_list = cmds.textScrollList(targetlist, q=True, ai=True)
    jointNum = len(t_list)
    
    print(t_list)
    print(t_joints)
    
    while i < len(t_joints):
        if t_list.count(t_joints[i]) == 0:
            t_joints.pop(i)
            i -= 1  
        else:
            if i < len(t_list):
                if t_list[i] == str(t_joints[i]):
                    i += 1
                    continue
                else:
                    j = i
                    while j < len(t_joints):
                        if t_list[i] == str(t_joints[j]):         
                            temp = t_joints[i]
                            t_joints[i] = t_joints[j]
                            t_joints[j] = temp
                            break
                        j += 1
    
    keyframes = pm.keyframe(sourceroot, query=True)
    keyframes = list(dict.fromkeys(keyframes))

    SetConstants(s_joints, t_joints)
    for key in keyframes:
        pm.currentTime(key)
        for i in range(len(s_joints)):
            SetRotation(s_joints[i], t_joints[i], key)
        t_joints[0].setTranslation(s_joints[0].getTranslation())
        t_joints[0].translate.setKey()


BuildUI()