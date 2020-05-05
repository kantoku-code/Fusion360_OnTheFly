#FusionAPI_python
#Author-kantoku
#Description-

import adsk.core, adsk.fusion, traceback
import math
from .Fusion360Utilities.Fusion360Utilities import AppObjects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase

# dialog
_selIptInfo = ['draftvec','角度基準','DraftVec']
_posInfo = ['pos', 'ﾏｳｽ3D座標値 :', 'Non!']
_draftInfo = ['draft', '角度 :', '-']
_draftRevInfo = ['draftrev', '反転 :', True]
_curvatureInfo = ['curvature', '最小R :', '-']
_curvatureRevInfo = ['curvaturerev', '反転 :', True]

_filter_face = ['BRepFace']

_uiView = None

def getVec_direction(ent) -> adsk.core.Vector3D:
    return ent.geometry.direction

def getVec_normal(ent) -> adsk.core.Vector3D:
    return ent.geometry.normal

def getVec_surface(ent) -> adsk.core.Vector3D:
    pnt = ent.pointOnFace
    eva = ent.evaluator
    _, vec = eva.getNormalAtPoint(pnt)
    return vec

def getVec_edge(ent) -> adsk.core.Vector3D:
    geo = ent.geometry
    return geo.startPoint.vectorTo(geo.endPoint)

def getVec_sktLine(ent) -> adsk.core.Vector3D:
    geo = ent.worldGeometry
    return geo.startPoint.vectorTo(geo.endPoint)

_filter_DraftVec = {
    'ConstructionPlane': getVec_normal,
    'ConstructionAxis': getVec_direction,
    # 'BRepFace' : getVec_surface,
    'BRepEdge': getVec_edge,
    'SketchLine' : getVec_sktLine}

class OnTheFlyCore(Fusion360CommandBase):
    _handlers = []

    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        pass

    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input, input_values):
        global _selIptInfo, _draftRevInfo, _curvatureRevInfo
        try:
            if changed_input.id == _selIptInfo[0]:
                print('on_input_changed-draft')
                # draft vec
                if changed_input.selectionCount < 1:
                    onFaceFactry.setDraftVec(None)
                    return
                
                ent = changed_input.selection(0).entity
                entType :str = ent.objectType.split('::')[-1]

                global _filter_DraftVec
                if not entType in _filter_DraftVec:
                    return
                
                fanc = _filter_DraftVec[entType]
                onFaceFactry.setDraftVec(fanc(ent))

            elif changed_input.id == _draftRevInfo[0]:
                # draft rev
                onFaceFactry._draftRev = changed_input.value

            elif changed_input.id == _curvatureRevInfo[0]:
                # curvature rev
                onFaceFactry._curvatureRev = changed_input.value

            # 更新
            global _uiView
            _uiView.upDateInfo(onFaceFactry.getInfo())

        except:
            print('Failed:\n{}'.format(traceback.format_exc()))
    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):

        command.isPositionDependent = True

        # -- dialog --
        global _uiView
        _uiView = uiView(inputs)
        command.isOKButtonVisible = False
        
        # -- Event --
        # MouseMove
        onMouseMove = MouseMoveHandler()
        command.mouseMove.add(onMouseMove)
        self._handlers.append(onMouseMove)

        # preSelect
        onFace = OnFaceHandler()
        command.preSelect.add(onFace)
        self._handlers.append(onFace)

        # -- Static class onFaceFactry --
        ao = AppObjects()
        onFaceFactry.setUnitsManager(ao.design.unitsManager)
        onFaceFactry.setDraftVec(None)

# MouseMoveｲﾍﾞﾝﾄ
class MouseMoveHandler(adsk.core.MouseEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args :adsk.core.MouseEventArgs):

        onFaceFactry.setMouse(
            args.viewport,
            args.viewportPosition)

        # 更新
        global _uiView
        _uiView.upDateInfo(onFaceFactry.getInfo())

# preSelectｲﾍﾞﾝﾄ
class OnFaceHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args :adsk.core.SelectionEventArgs):
        try:
            try:
                sel = args.selection
                ent = sel.entity
                entType :str = ent.objectType.split('::')[-1]

                # 面取得
                global _filter_face
                if entType in _filter_face:
                    onFaceFactry.setFace(ent)

                # 角度基準
                global _filter_DraftVec
                if entType in _filter_DraftVec:
                    if entType == 'BRepFace':
                        geo = ent.geometry
                        geoType = geo.surfaceType
                        flat = adsk.core.SurfaceTypes.PlaneSurfaceType
                        args.isSelectable = True if geoType == flat else False

                    elif entType == 'BRepEdge':
                        geo = adsk.core.Line3D.cast(ent.geometry)
                        args.isSelectable = True if geo else False

                    else:
                        args.isSelectable = True

                else:
                    # それ以外
                    args.isSelectable = False

            except:
                args.isSelectable = False

            # 更新
            global _uiView
            _uiView.upDateInfo(onFaceFactry.getInfo())
        except:
            ao = AppObjects()
            ao.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# ﾀﾞｲｱﾛｸﾞ管理
class uiView():
    def __init__(self, inputs :adsk.core.CommandInputs):
        self.pos = inputs.addTextBoxCommandInput(_posInfo[0], _posInfo[1], _posInfo[2], 1, True)

        self.draftVec = inputs.addSelectionInput(_selIptInfo[0], _selIptInfo[1], _selIptInfo[2])
        self.draft = inputs.addTextBoxCommandInput(_draftInfo[0], _draftInfo[1], _draftInfo[2], 1, True)
        self.draftRev = inputs.addBoolValueInput(_draftRevInfo[0], _draftRevInfo[1], _draftRevInfo[2])

        self.curvature = inputs.addTextBoxCommandInput(_curvatureInfo[0], _curvatureInfo[1], _curvatureInfo[2], 1, True)
        self.curvatureRev = inputs.addBoolValueInput(_curvatureRevInfo[0], _curvatureRevInfo[1], _curvatureRevInfo[2])

    def upDateInfo(self, info :list):
        self.pos.text = info[0]
        self.draft.text = info[1]
        self.curvature.text = info[2]

        self.draftVec.commandPrompt = '{}\n{}'.format(info[1], info[2])


# 現状と管理し情報を垂れ流す
class onFaceFactry:
    _vp = adsk.core.Viewport.cast(None) 
    _face = adsk.fusion.BRepFace.cast(None)
    _clone = adsk.fusion.BRepFace.cast(None)
    _musPos = adsk.core.Point2D.cast(None)
    _draftVec = adsk.core.Vector3D.cast(None)
    _draftRev = False
    _curvatureRev = False
    _covunit = 0.0
    _defLenUnit = ''

    @classmethod
    def setUnitsManager(cls, um :adsk.core.UnitsManager):
        cls._defLenUnit = um.defaultLengthUnits
        cls._covunit = um.convert(1, um.internalUnits, cls._defLenUnit)

    @classmethod
    def setMouse(cls, vp :adsk.core.Viewport, musPos :adsk.core.Point2D):
        cls._vp = vp
        cls._musPos = musPos

    @classmethod
    def setFace(cls, face :adsk.fusion.BRepFace):
        if cls._face == face:
            return

        cls._face = face

        if face:
            tmpBrep = adsk.fusion.TemporaryBRepManager.get()
            cloneBody = tmpBrep.copy(face)
            cls._clone = cloneBody.faces[0]
        else:
            cls._clone = None

    @classmethod
    def setDraftVec(cls, vec :adsk.core.Vector3D):
        if vec:
            cls._draftVec = vec
        else:
            cls._draftVec = adsk.core.Vector3D.create(0.0, 0.0, 1.0)

    @classmethod
    def setDraftRev(cls,  yn :bool):
        cls._draftRev = yn

    @classmethod
    def setCurvatureRev(cls, yn :bool):
        cls._curvatureRev = yn

    @classmethod
    def getInfo(cls):
        try:
            # 交点
            pos3d = cls._vp.viewToModelSpace(cls._musPos)
            cam = cls._vp.camera
            vec = cam.eye.vectorTo(cam.target)
        
            musPnt = adsk.core.Point3D.create(
                pos3d.x + vec.x, 
                pos3d.y + vec.y, 
                pos3d.z + vec.z)
            
            musInf =  adsk.core.Line3D.create(pos3d, musPnt).asInfiniteLine()
            if not cls._clone:
                return ['Non!', '-' , '-'] #仮設定

            geo :adsk.core.Surface = cls._clone.geometry
            
            ints = musInf.intersectWithSurface(geo)
            if ints.count < 1:
                return ['Non!', '-' , '-']

            # 一番近い点
            pnt :adsk.core.Point3D = min(ints, key = (lambda p:cam.eye.distanceTo(p)))
            pnt_txt = 'x:{:.3f} y:{:.3f} z:{:.3f}'.format(
                    pnt.x * cls._covunit,
                    pnt.y * cls._covunit,
                    pnt.z * cls._covunit)

            # evaluator
            eva :adsk.core.SurfaceEvaluator = cls._clone.evaluator
            res, prm = eva.getParameterAtPoint(pnt)
            if not res:
                return ['Non!', '-' , '-']

            if not eva.isParameterOnFace(prm):
                return ['Non!', '-' , '-']

            # 法線
            res, normal = eva.getNormalAtParameter(prm)
            if not res:
                return [pnt_txt, '-' , '-']
            draft = cls._draftVec.angleTo(normal)

            if draft > math.pi * 0.5 :
                dfrev = -1 if cls._draftRev else 1
                draft = ((math.pi * -1) + draft) * dfrev

            draft_txt = '{:.3f} deg'.format(math.degrees(draft))

            # 曲率
            # if geo.classType() == 'adsk::core::Plane':
            #     return [pnt_txt, draft_txt , '-']

            res, maxTangent, maxCrv, minCrv = eva.getCurvature(prm)
            if not res:
                return [pnt_txt, draft_txt , '-']

            if round(maxCrv, 4) != 0 :
                ctrev = -1 if cls._curvatureRev else 1
                crv_txt = '{:.3f}{}'.format(
                        (1 / maxCrv * cls._covunit * -1) * ctrev, 
                        cls._defLenUnit)
            else:
                crv_txt = '-'

            return [pnt_txt, draft_txt , crv_txt]

        except:
            print('infoNG')
            return ['Non!', '-' , '-']