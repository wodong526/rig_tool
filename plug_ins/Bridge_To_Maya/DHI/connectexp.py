import pymel.core as pycore
from pymel.core.language import mel
from DHI.modules.maya.util import MayaUtil

try:
    # Python 2
    xrange
except NameError:
    # Python 3, xrange is now named range
    xrange = range

# ****************************************************************************************************
def defaultLambertShader():
    meshes = ["head_lod0_mesh", "teeth_lod0_mesh", "saliva_lod0_mesh", "eyeLeft_lod0_mesh", "eyeRight_lod0_mesh",
              "eyeshell_lod0_mesh", "eyelashes_lod0_mesh", "eyeEdge_lod0_mesh"]
    for mesh in meshes:
        try:
            pycore.select(mesh, r=True)
            mel.eval("sets -e -forceElement initialShadingGroup")
        except Exception as ex:
            print ("couldn't set lambert shader for mesh ", mesh)
            print ("Reason: ", ex)


# ****************************************************************************************************
def connectExpression(driverCtrl, driverAttr, minVal, maxVal, driverKey1, driverKey2, expCtrl, expAttr, expKey1,
                      expKey2):
    # create driver attribute if dont exists
    if not pycore.objExists(driverCtrl + "." + driverAttr):
        pycore.addAttr(driverCtrl, longName=driverAttr, keyable=True, attributeType="float", minValue=minVal,
                       maxValue=maxVal, dv=0.0)

    # connect CTRL driver with driven expression
    pycore.setDrivenKeyframe((expCtrl + "." + expAttr), itt="linear", ott="linear",
                             currentDriver=(driverCtrl + "." + driverAttr), driverValue=driverKey1, value=expKey1)
    pycore.setDrivenKeyframe((expCtrl + "." + expAttr), itt="linear", ott="linear",
                             currentDriver=(driverCtrl + "." + driverAttr), driverValue=driverKey2, value=expKey2)


# ****************************************************************************************************
def connectAllExpressions():
    # brows down
    connectExpression("CTRL_L_brow_down", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "browDownL", 0.0, 1.0)
    connectExpression("CTRL_R_brow_down", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "browDownR", 0.0, 1.0)
    # brows lateral
    connectExpression("CTRL_L_brow_lateral", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "browLateralL", 0.0, 1.0)
    connectExpression("CTRL_R_brow_lateral", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "browLateralR", 0.0, 1.0)
    # brows raise
    connectExpression("CTRL_L_brow_raiseIn", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "browRaiseInL", 0.0, 1.0)
    connectExpression("CTRL_R_brow_raiseIn", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "browRaiseInR", 0.0, 1.0)
    connectExpression("CTRL_L_brow_raiseOut", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "browRaiseOuterL", 0.0, 1.0)
    connectExpression("CTRL_R_brow_raiseOut", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "browRaiseOuterR", 0.0, 1.0)
    # ears up
    connectExpression("CTRL_L_ear_up", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "earUpL", 0.0, 1.0)
    connectExpression("CTRL_R_ear_up", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "earUpR", 0.0, 1.0)
    # eyes widen/blink
    connectExpression("CTRL_L_eye_blink", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeBlinkL", 0.0, 1.0)
    connectExpression("CTRL_R_eye_blink", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeBlinkR", 0.0, 1.0)
    connectExpression("CTRL_L_eye_blink", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "eyeWidenL", 0.0, 1.0)
    connectExpression("CTRL_R_eye_blink", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "eyeWidenR", 0.0, 1.0)
    # lid press
    connectExpression("CTRL_L_eye_lidPress", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeLidPressL", 0.0, 1.0)
    connectExpression("CTRL_R_eye_lidPress", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeLidPressR", 0.0, 1.0)
    # eyes squint inner
    connectExpression("CTRL_L_eye_squintInner", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeSquintInnerL", 0.0,
                      1.0)
    connectExpression("CTRL_R_eye_squintInner", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeSquintInnerR", 0.0,
                      1.0)
    # eyes cheek raise
    connectExpression("CTRL_L_eye_cheekRaise", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeCheekRaiseL", 0.0, 1.0)
    connectExpression("CTRL_R_eye_cheekRaise", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeCheekRaiseR", 0.0, 1.0)
    # face scrunch
    connectExpression("CTRL_L_eye_faceScrunch", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeFaceScrunchL", 0.0,
                      1.0)
    connectExpression("CTRL_R_eye_faceScrunch", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeFaceScrunchR", 0.0,
                      1.0)
    # eyelids up/down (and eyes relax)
    connectExpression("CTRL_L_eye_eyelidU", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "eyeUpperLidUpL", 0.0, 1.0)
    connectExpression("CTRL_R_eye_eyelidU", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "eyeUpperLidUpR", 0.0, 1.0)
    connectExpression("CTRL_L_eye_eyelidU", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeRelaxL", 0.0, 1.0)
    connectExpression("CTRL_R_eye_eyelidU", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeRelaxR", 0.0, 1.0)
    connectExpression("CTRL_L_eye_eyelidD", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "eyeLowerLidDownL", 0.0,
                      1.0)
    connectExpression("CTRL_R_eye_eyelidD", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "eyeLowerLidDownR", 0.0,
                      1.0)
    connectExpression("CTRL_L_eye_eyelidD", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeLowerLidUpL", 0.0, 1.0)
    connectExpression("CTRL_R_eye_eyelidD", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyeLowerLidUpR", 0.0, 1.0)
    # eyes look up/down/left/right
    connectExpression("LOC_L_eyeDriver", "rx", -30.0, 40.0, 0.0, -30.0, "CTRL_expressions", "eyeLookUpL", 0.0, 1.0)
    connectExpression("LOC_R_eyeDriver", "rx", -30.0, 40.0, 0.0, -30.0, "CTRL_expressions", "eyeLookUpR", 0.0, 1.0)
    connectExpression("LOC_L_eyeDriver", "rx", -30.0, 40.0, 0.0, 40.0, "CTRL_expressions", "eyeLookDownL", 0.0, 1.0)
    connectExpression("LOC_R_eyeDriver", "rx", -30.0, 40.0, 0.0, 40.0, "CTRL_expressions", "eyeLookDownR", 0.0, 1.0)
    connectExpression("LOC_L_eyeDriver", "ry", -40.0, 40.0, 0.0, 40.0, "CTRL_expressions", "eyeLookLeftL", 0.0, 1.0)
    connectExpression("LOC_R_eyeDriver", "ry", -40.0, 40.0, 0.0, 40.0, "CTRL_expressions", "eyeLookLeftR", 0.0, 1.0)
    connectExpression("LOC_L_eyeDriver", "ry", -40.0, 40.0, 0.0, -40.0, "CTRL_expressions", "eyeLookRightL", 0.0, 1.0)
    connectExpression("LOC_R_eyeDriver", "ry", -40.0, 40.0, 0.0, -40.0, "CTRL_expressions", "eyeLookRightR", 0.0, 1.0)
    # pupils wide/narrow
    connectExpression("CTRL_L_eye_pupil", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyePupilWideL", 0.0, 1.0)
    connectExpression("CTRL_R_eye_pupil", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyePupilWideR", 0.0, 1.0)
    connectExpression("CTRL_L_eye_pupil", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "eyePupilNarrowL", 0.0, 1.0)
    connectExpression("CTRL_R_eye_pupil", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "eyePupilNarrowR", 0.0, 1.0)
    # eyes parallel
    connectExpression("CTRL_C_eye_parallelLook", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "eyeParallelLookDirection", 0.0, 1.0)
    # eyelashes tweakers
    connectExpression("CTRL_L_eyelashes_tweakerIn", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyelashesDownINL",
                      0.0, 1.0)
    connectExpression("CTRL_R_eyelashes_tweakerIn", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyelashesDownINR",
                      0.0, 1.0)
    connectExpression("CTRL_L_eyelashes_tweakerOut", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyelashesDownOUTL",
                      0.0, 1.0)
    connectExpression("CTRL_R_eyelashes_tweakerOut", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "eyelashesDownOUTR",
                      0.0, 1.0)
    connectExpression("CTRL_L_eyelashes_tweakerIn", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "eyelashesUpINL",
                      0.0, 1.0)
    connectExpression("CTRL_R_eyelashes_tweakerIn", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "eyelashesUpINR",
                      0.0, 1.0)
    connectExpression("CTRL_L_eyelashes_tweakerOut", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "eyelashesUpOUTL",
                      0.0, 1.0)
    connectExpression("CTRL_R_eyelashes_tweakerOut", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "eyelashesUpOUTR",
                      0.0, 1.0)
    # nose wrinkle/depress/dilate/compress
    connectExpression("CTRL_L_nose", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "noseWrinkleL", 0.0, 1.0)
    connectExpression("CTRL_R_nose", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "noseWrinkleR", 0.0, 1.0)
    connectExpression("CTRL_L_nose", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "noseNostrilDepressL", 0.0, 1.0)
    connectExpression("CTRL_R_nose", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "noseNostrilDepressR", 0.0, 1.0)
    connectExpression("CTRL_L_nose", "tx", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "noseNostrilDilateL", 0.0, 1.0)
    connectExpression("CTRL_R_nose", "tx", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "noseNostrilDilateR", 0.0, 1.0)
    connectExpression("CTRL_L_nose", "tx", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "noseNostrilCompressL", 0.0, 1.0)
    connectExpression("CTRL_R_nose", "tx", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "noseNostrilCompressR", 0.0, 1.0)
    # nose wrinkle upper
    connectExpression("CTRL_L_nose_wrinkleUpper", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "noseWrinkleUpperL",
                      0.0, 1.0)
    connectExpression("CTRL_R_nose_wrinkleUpper", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "noseWrinkleUpperR",
                      0.0, 1.0)
    # nasolabial deepener
    connectExpression("CTRL_L_nose_nasolabialDeepen", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "noseNasolabialDeepenL", 0.0, 1.0)
    connectExpression("CTRL_R_nose_nasolabialDeepen", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "noseNasolabialDeepenR", 0.0, 1.0)
    # cheek suck/blow
    connectExpression("CTRL_L_mouth_suckBlow", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthCheekBlowL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_suckBlow", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthCheekBlowR", 0.0,
                      1.0)
    connectExpression("CTRL_L_mouth_suckBlow", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthCheekSuckL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_suckBlow", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthCheekSuckR", 0.0,
                      1.0)
    # lips blow
    connectExpression("CTRL_L_mouth_lipsBlow", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsBlowL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_lipsBlow", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsBlowR", 0.0, 1.0)
    # mouth up/down/left/right
    connectExpression("CTRL_C_mouth", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthUp", 0.0, 1.0)
    connectExpression("CTRL_C_mouth", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthDown", 0.0, 1.0)
    connectExpression("CTRL_C_mouth", "tx", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLeft", 0.0, 1.0)
    connectExpression("CTRL_C_mouth", "tx", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthRight", 0.0, 1.0)
    # upper lip raise
    connectExpression("CTRL_L_mouth_upperLipRaise", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthUpperLipRaiseL",
                      0.0, 1.0)
    connectExpression("CTRL_R_mouth_upperLipRaise", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthUpperLipRaiseR",
                      0.0, 1.0)
    # lower lip depress
    connectExpression("CTRL_L_mouth_lowerLipDepress", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthLowerLipDepressL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_lowerLipDepress", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthLowerLipDepressR", 0.0, 1.0)
    # corner pull
    connectExpression("CTRL_L_mouth_cornerPull", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthCornerPullL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_cornerPull", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthCornerPullR", 0.0,
                      1.0)
    # mouth stretch
    connectExpression("CTRL_L_mouth_stretch", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthStretchL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_stretch", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthStretchR", 0.0, 1.0)
    # mouth stretch lips close
    connectExpression("CTRL_L_mouth_stretchLipsClose", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthStretchLipsCloseL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_stretchLipsClose", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthStretchLipsCloseR", 0.0, 1.0)
    # dimpler
    connectExpression("CTRL_L_mouth_dimple", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthDimpleL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_dimple", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthDimpleR", 0.0, 1.0)
    # corner depress
    connectExpression("CTRL_L_mouth_cornerDepress", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthCornerDepressL",
                      0.0, 1.0)
    connectExpression("CTRL_R_mouth_cornerDepress", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthCornerDepressR",
                      0.0, 1.0)
    # mouth press
    connectExpression("CTRL_L_mouth_pressU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthPressUL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_pressU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthPressUR", 0.0, 1.0)
    connectExpression("CTRL_L_mouth_pressD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthPressDL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_pressD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthPressDR", 0.0, 1.0)
    # purse
    connectExpression("CTRL_L_mouth_purseU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsPurseUL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_purseU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsPurseUR", 0.0, 1.0)
    connectExpression("CTRL_L_mouth_purseD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsPurseDL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_purseD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsPurseDR", 0.0, 1.0)
    # lips towards
    connectExpression("CTRL_L_mouth_towardsU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsTowardsUL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_towardsU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsTowardsUR", 0.0,
                      1.0)
    connectExpression("CTRL_L_mouth_towardsD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsTowardsDL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_towardsD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsTowardsDR", 0.0,
                      1.0)
    # funnel
    connectExpression("CTRL_L_mouth_funnelU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthFunnelUL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_funnelU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthFunnelUR", 0.0, 1.0)
    connectExpression("CTRL_L_mouth_funnelD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthFunnelDL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_funnelD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthFunnelDR", 0.0, 1.0)
    # lips together
    connectExpression("CTRL_L_mouth_lipsTogetherU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsTogetherUL",
                      0.0, 1.0)
    connectExpression("CTRL_R_mouth_lipsTogetherU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsTogetherUR",
                      0.0, 1.0)
    connectExpression("CTRL_L_mouth_lipsTogetherD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsTogetherDL",
                      0.0, 1.0)
    connectExpression("CTRL_R_mouth_lipsTogetherD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsTogetherDR",
                      0.0, 1.0)
    # upper lip bite
    connectExpression("CTRL_L_mouth_lipBiteU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthUpperLipBiteL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_lipBiteU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthUpperLipBiteR", 0.0,
                      1.0)
    # lower lip bite
    connectExpression("CTRL_L_mouth_lipBiteD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLowerLipBiteL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_lipBiteD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLowerLipBiteR", 0.0,
                      1.0)
    # lips tighten
    connectExpression("CTRL_L_mouth_tightenU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsTightenUL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_tightenU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsTightenUR", 0.0,
                      1.0)
    connectExpression("CTRL_L_mouth_tightenD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsTightenDL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_tightenD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsTightenDR", 0.0,
                      1.0)
    # lips press
    connectExpression("CTRL_L_mouth_lipsPressU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsPressL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_lipsPressU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsPressR", 0.0,
                      1.0)
    # sharp corner pull
    connectExpression("CTRL_L_mouth_sharpCornerPull", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthSharpCornerPullL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_sharpCornerPull", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthSharpCornerPullR", 0.0, 1.0)
    # mouth sticky
    connectExpression("CTRL_C_mouth_stickyU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthStickyUC", 0.0, 1.0)
    connectExpression("CTRL_L_mouth_stickyInnerU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthStickyUINL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_stickyInnerU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthStickyUINR", 0.0,
                      1.0)
    connectExpression("CTRL_L_mouth_stickyOuterU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthStickyUOUTL",
                      0.0, 1.0)
    connectExpression("CTRL_R_mouth_stickyOuterU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthStickyUOUTR",
                      0.0, 1.0)
    connectExpression("CTRL_C_mouth_stickyD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthStickyDC", 0.0, 1.0)
    connectExpression("CTRL_L_mouth_stickyInnerD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthStickyDINL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_stickyInnerD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthStickyDINR", 0.0,
                      1.0)
    connectExpression("CTRL_L_mouth_stickyOuterD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthStickyDOUTL",
                      0.0, 1.0)
    connectExpression("CTRL_R_mouth_stickyOuterD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthStickyDOUTR",
                      0.0, 1.0)
    # sticky lips
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyLPh1", itt="linear", ott="linear",
                             currentDriver="CTRL_L_mouth_lipSticky.ty", driverValue=0, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyLPh1", itt="linear", ott="linear",
                             currentDriver="CTRL_L_mouth_lipSticky.ty", driverValue=0.33, value=1)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyLPh1", itt="linear", ott="linear",
                             currentDriver="CTRL_L_mouth_lipSticky.ty", driverValue=0.66, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyLPh2", itt="linear", ott="linear",
                             currentDriver="CTRL_L_mouth_lipSticky.ty", driverValue=0.33, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyLPh2", itt="linear", ott="linear",
                             currentDriver="CTRL_L_mouth_lipSticky.ty", driverValue=0.66, value=1)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyLPh2", itt="linear", ott="linear",
                             currentDriver="CTRL_L_mouth_lipSticky.ty", driverValue=1, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyLPh3", itt="linear", ott="linear",
                             currentDriver="CTRL_L_mouth_lipSticky.ty", driverValue=0.66, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyLPh3", itt="linear", ott="linear",
                             currentDriver="CTRL_L_mouth_lipSticky.ty", driverValue=1, value=1)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyRPh1", itt="linear", ott="linear",
                             currentDriver="CTRL_R_mouth_lipSticky.ty", driverValue=0, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyRPh1", itt="linear", ott="linear",
                             currentDriver="CTRL_R_mouth_lipSticky.ty", driverValue=0.33, value=1)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyRPh1", itt="linear", ott="linear",
                             currentDriver="CTRL_R_mouth_lipSticky.ty", driverValue=0.66, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyRPh2", itt="linear", ott="linear",
                             currentDriver="CTRL_R_mouth_lipSticky.ty", driverValue=0.33, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyRPh2", itt="linear", ott="linear",
                             currentDriver="CTRL_R_mouth_lipSticky.ty", driverValue=0.66, value=1)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyRPh2", itt="linear", ott="linear",
                             currentDriver="CTRL_R_mouth_lipSticky.ty", driverValue=1, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyRPh3", itt="linear", ott="linear",
                             currentDriver="CTRL_R_mouth_lipSticky.ty", driverValue=0.66, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.mouthLipsStickyRPh3", itt="linear", ott="linear",
                             currentDriver="CTRL_R_mouth_lipSticky.ty", driverValue=1, value=1)
    # lips push/pull
    connectExpression("CTRL_L_mouth_pushPullU", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsPushUL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_pushPullU", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsPushUR", 0.0,
                      1.0)
    connectExpression("CTRL_L_mouth_pushPullD", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsPushDL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_pushPullD", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsPushDR", 0.0,
                      1.0)
    connectExpression("CTRL_L_mouth_pushPullU", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthLipsPullUL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_pushPullU", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthLipsPullUR", 0.0,
                      1.0)
    connectExpression("CTRL_L_mouth_pushPullD", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthLipsPullDL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_pushPullD", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthLipsPullDR", 0.0,
                      1.0)
    # lips thin/thick
    connectExpression("CTRL_L_mouth_thicknessU", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsThinUL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_thicknessU", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsThinUR", 0.0,
                      1.0)
    connectExpression("CTRL_L_mouth_thicknessD", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsThinDL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_thicknessD", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLipsThinDR", 0.0,
                      1.0)
    connectExpression("CTRL_L_mouth_thicknessU", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthLipsThickUL",
                      0.0, 1.0)
    connectExpression("CTRL_R_mouth_thicknessU", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthLipsThickUR",
                      0.0, 1.0)
    connectExpression("CTRL_L_mouth_thicknessD", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthLipsThickDL",
                      0.0, 1.0)
    connectExpression("CTRL_R_mouth_thicknessD", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthLipsThickDR",
                      0.0, 1.0)
    # corner sharpen
    connectExpression("CTRL_L_mouth_cornerSharpnessU", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthCornerSharpenUL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_cornerSharpnessU", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthCornerSharpenUR", 0.0, 1.0)
    connectExpression("CTRL_L_mouth_cornerSharpnessD", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthCornerSharpenDL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_cornerSharpnessD", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthCornerSharpenDR", 0.0, 1.0)
    connectExpression("CTRL_L_mouth_cornerSharpnessU", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions",
                      "mouthCornerRounderUL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_cornerSharpnessU", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions",
                      "mouthCornerRounderUR", 0.0, 1.0)
    connectExpression("CTRL_L_mouth_cornerSharpnessD", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions",
                      "mouthCornerRounderDL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_cornerSharpnessD", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions",
                      "mouthCornerRounderDR", 0.0, 1.0)
    # lips towards
    connectExpression("CTRL_L_mouth_lipsTowardsTeethU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthUpperLipTowardsTeethL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_lipsTowardsTeethU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthUpperLipTowardsTeethR", 0.0, 1.0)
    connectExpression("CTRL_L_mouth_lipsTowardsTeethD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthLowerLipTowardsTeethL", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_lipsTowardsTeethD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "mouthLowerLipTowardsTeethR", 0.0, 1.0)
    # lips shift
    connectExpression("CTRL_C_mouth_lipShiftU", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthUpperLipShiftLeft",
                      0.0, 1.0)
    connectExpression("CTRL_C_mouth_lipShiftU", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions",
                      "mouthUpperLipShiftRight", 0.0, 1.0)
    connectExpression("CTRL_C_mouth_lipShiftD", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLowerLipShiftLeft",
                      0.0, 1.0)
    connectExpression("CTRL_C_mouth_lipShiftD", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions",
                      "mouthLowerLipShiftRight", 0.0, 1.0)
    # lips roll
    connectExpression("CTRL_L_mouth_lipsRollU", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthUpperLipRollInL",
                      0.0, 1.0)
    connectExpression("CTRL_R_mouth_lipsRollU", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthUpperLipRollInR",
                      0.0, 1.0)
    connectExpression("CTRL_L_mouth_lipsRollD", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLowerLipRollInL",
                      0.0, 1.0)
    connectExpression("CTRL_R_mouth_lipsRollD", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthLowerLipRollInR",
                      0.0, 1.0)
    connectExpression("CTRL_L_mouth_lipsRollU", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthUpperLipRollOutL",
                      0.0, 1.0)
    connectExpression("CTRL_R_mouth_lipsRollU", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthUpperLipRollOutR",
                      0.0, 1.0)
    connectExpression("CTRL_L_mouth_lipsRollD", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthLowerLipRollOutL",
                      0.0, 1.0)
    connectExpression("CTRL_R_mouth_lipsRollD", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthLowerLipRollOutR",
                      0.0, 1.0)
    # corners
    connectExpression("CTRL_L_mouth_corner", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthCornerUpL", 0.0, 1.0)
    connectExpression("CTRL_L_mouth_corner", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthCornerDownL", 0.0,
                      1.0)
    connectExpression("CTRL_L_mouth_corner", "tx", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthCornerWideL", 0.0,
                      1.0)
    connectExpression("CTRL_L_mouth_corner", "tx", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthCornerNarrowL", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_corner", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthCornerUpR", 0.0, 1.0)
    connectExpression("CTRL_R_mouth_corner", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthCornerDownR", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_corner", "tx", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "mouthCornerWideR", 0.0,
                      1.0)
    connectExpression("CTRL_R_mouth_corner", "tx", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "mouthCornerNarrowR", 0.0,
                      1.0)
    # tongue up/down/left/right
    connectExpression("CTRL_C_tongue", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "tongueUp", 0.0, 1.0)
    connectExpression("CTRL_C_tongue", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "tongueDown", 0.0, 1.0)
    connectExpression("CTRL_C_tongue", "tx", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "tongueLeft", 0.0, 1.0)
    connectExpression("CTRL_C_tongue", "tx", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "tongueRight", 0.0, 1.0)
    # tongue roll up/down/left/right
    connectExpression("CTRL_C_tongue_roll", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "tongueRollUp", 0.0, 1.0)
    connectExpression("CTRL_C_tongue_roll", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "tongueRollDown", 0.0, 1.0)
    connectExpression("CTRL_C_tongue_roll", "tx", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "tongueRollLeft", 0.0, 1.0)
    connectExpression("CTRL_C_tongue_roll", "tx", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "tongueRollRight", 0.0, 1.0)
    # tongue tip up/down/left/right
    connectExpression("CTRL_C_tongue_tip", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "tongueTipUp", 0.0, 1.0)
    connectExpression("CTRL_C_tongue_tip", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "tongueTipDown", 0.0, 1.0)
    connectExpression("CTRL_C_tongue_tip", "tx", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "tongueTipLeft", 0.0, 1.0)
    connectExpression("CTRL_C_tongue_tip", "tx", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "tongueTipRight", 0.0, 1.0)
    # tongue in/out
    connectExpression("CTRL_C_tongue_inOut", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "tongueIn", 0.0, 1.0)
    connectExpression("CTRL_C_tongue_inOut", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "tongueOut", 0.0, 1.0)
    # tongue press
    connectExpression("CTRL_C_tongue_press", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "tonguePress", 0.0, 1.0)
    # tongue wide/narrow
    connectExpression("CTRL_C_tongue_narrowWide", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "tongueWide", 0.0, 1.0)
    connectExpression("CTRL_C_tongue_narrowWide", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "tongueNarrow", 0.0,
                      1.0)
    # jaw open
    connectExpression("CTRL_C_jaw", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "jawOpen", 0.0, 1.0)
    # jaw left/right
    connectExpression("CTRL_C_jaw", "tx", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "jawLeft", 0.0, 1.0)
    connectExpression("CTRL_C_jaw", "tx", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "jawRight", 0.0, 1.0)
    # jaw back/fwd
    connectExpression("CTRL_C_jaw_fwdBack", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "jawFwd", 0.0, 1.0)
    connectExpression("CTRL_C_jaw_fwdBack", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "jawBack", 0.0, 1.0)
    # jaw clench
    connectExpression("CTRL_L_jaw_clench", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "jawClenchL", 0.0, 1.0)
    connectExpression("CTRL_R_jaw_clench", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "jawClenchR", 0.0, 1.0)
    # chin raise
    connectExpression("CTRL_L_jaw_ChinRaiseU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "jawChinRaiseUL", 0.0, 1.0)
    connectExpression("CTRL_R_jaw_ChinRaiseU", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "jawChinRaiseUR", 0.0, 1.0)
    connectExpression("CTRL_L_jaw_ChinRaiseD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "jawChinRaiseDL", 0.0, 1.0)
    connectExpression("CTRL_R_jaw_ChinRaiseD", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "jawChinRaiseDR", 0.0, 1.0)
    # chin compress
    connectExpression("CTRL_L_jaw_chinCompress", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "jawChinCompressL", 0.0,
                      1.0)
    connectExpression("CTRL_R_jaw_chinCompress", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "jawChinCompressR", 0.0,
                      1.0)
    # jaw open extreme
    connectExpression("CTRL_C_jaw_openExtreme", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "jawOpenExtreme", 0.0,
                      1.0)
    # neck stretch
    connectExpression("CTRL_L_neck_stretch", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "neckStretchL", 0.0, 1.0)
    connectExpression("CTRL_R_neck_stretch", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "neckStretchR", 0.0, 1.0)
    # swallow
    pycore.setDrivenKeyframe("CTRL_expressions.neckSwallowPh1", itt="linear", ott="linear",
                             currentDriver="CTRL_C_neck_swallow.ty", driverValue=0, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.neckSwallowPh1", itt="linear", ott="linear",
                             currentDriver="CTRL_C_neck_swallow.ty", driverValue=0.2, value=1)
    pycore.setDrivenKeyframe("CTRL_expressions.neckSwallowPh1", itt="linear", ott="linear",
                             currentDriver="CTRL_C_neck_swallow.ty", driverValue=0.4, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.neckSwallowPh2", itt="linear", ott="linear",
                             currentDriver="CTRL_C_neck_swallow.ty", driverValue=0.2, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.neckSwallowPh2", itt="linear", ott="linear",
                             currentDriver="CTRL_C_neck_swallow.ty", driverValue=0.4, value=1)
    pycore.setDrivenKeyframe("CTRL_expressions.neckSwallowPh2", itt="linear", ott="linear",
                             currentDriver="CTRL_C_neck_swallow.ty", driverValue=0.6, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.neckSwallowPh3", itt="linear", ott="linear",
                             currentDriver="CTRL_C_neck_swallow.ty", driverValue=0.4, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.neckSwallowPh3", itt="linear", ott="linear",
                             currentDriver="CTRL_C_neck_swallow.ty", driverValue=0.6, value=1)
    pycore.setDrivenKeyframe("CTRL_expressions.neckSwallowPh3", itt="linear", ott="linear",
                             currentDriver="CTRL_C_neck_swallow.ty", driverValue=0.8, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.neckSwallowPh4", itt="linear", ott="linear",
                             currentDriver="CTRL_C_neck_swallow.ty", driverValue=0.6, value=0)
    pycore.setDrivenKeyframe("CTRL_expressions.neckSwallowPh4", itt="linear", ott="linear",
                             currentDriver="CTRL_C_neck_swallow.ty", driverValue=0.8, value=1)
    pycore.setDrivenKeyframe("CTRL_expressions.neckSwallowPh4", itt="linear", ott="linear",
                             currentDriver="CTRL_C_neck_swallow.ty", driverValue=1, value=0)
    # mastoid contract
    connectExpression("CTRL_L_neck_mastoidContract", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "neckMastoidContractL", 0.0, 1.0)
    connectExpression("CTRL_R_neck_mastoidContract", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions",
                      "neckMastoidContractR", 0.0, 1.0)
    # throat down/up
    connectExpression("CTRL_neck_throatUpDown", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "neckThroatDown", 0.0,
                      1.0)
    connectExpression("CTRL_neck_throatUpDown", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "neckThroatUp", 0.0, 1.0)
    # digastric down/up
    connectExpression("CTRL_neck_digastricUpDown", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "neckDigastricDown",
                      0.0, 1.0)
    connectExpression("CTRL_neck_digastricUpDown", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "neckDigastricUp",
                      0.0, 1.0)
    # exale/inhale
    connectExpression("CTRL_neck_throatExhaleInhale", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions",
                      "neckThroatExhale", 0.0, 1.0)
    connectExpression("CTRL_neck_throatExhaleInhale", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "neckThroatInhale",
                      0.0, 1.0)
    '''
    # head turns
    connectExpression("CTRL_C_headTurns", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "headTurnUp", 0.0, 1.0)
    connectExpression("CTRL_C_headTurns", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "headTurnDown", 0.0, 1.0)
    connectExpression("CTRL_C_headTurns", "tx", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "headTurnLeft", 0.0, 1.0)
    connectExpression("CTRL_C_headTurns", "tx", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "headTurnRight", 0.0, 1.0)
    connectExpression("CTRL_C_headTilts", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "headTiltRight", 0.0, 1.0)
    connectExpression("CTRL_C_headTilts", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "headTiltLeft", 0.0, 1.0)
    connectExpression("CTRL_C_headBackFwd", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "headFwd", 0.0, 1.0)
    connectExpression("CTRL_C_headBackFwd", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "headBack", 0.0, 1.0)
    '''
    # upper teeth
    connectExpression("CTRL_C_teethU", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "teethUpU", 0.0, 1.0)
    connectExpression("CTRL_C_teethU", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "teethDownU", 0.0, 1.0)
    connectExpression("CTRL_C_teethU", "tx", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "teethLeftU", 0.0, 1.0)
    connectExpression("CTRL_C_teethU", "tx", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "teethRightU", 0.0, 1.0)
    connectExpression("CTRL_C_teeth_fwdBackU", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "teethBackU", 0.0, 1.0)
    connectExpression("CTRL_C_teeth_fwdBackU", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "teethFwdU", 0.0, 1.0)
    # lower teeth
    connectExpression("CTRL_C_teethD", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "teethUpD", 0.0, 1.0)
    connectExpression("CTRL_C_teethD", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "teethDownD", 0.0, 1.0)
    connectExpression("CTRL_C_teethD", "tx", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "teethLeftD", 0.0, 1.0)
    connectExpression("CTRL_C_teethD", "tx", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "teethRightD", 0.0, 1.0)
    connectExpression("CTRL_C_teeth_fwdBackD", "ty", -1.0, 1.0, 0.0, 1.0, "CTRL_expressions", "teethBackD", 0.0, 1.0)
    connectExpression("CTRL_C_teeth_fwdBackD", "ty", -1.0, 1.0, 0.0, -1.0, "CTRL_expressions", "teethFwdD", 0.0, 1.0)
    # rig logic off on
    # connectExpression("CTRL_rigLogicSwitch", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_rigLogic", "OffOn", 0.0, 1.0)
    # look at switch
    pycore.addAttr("CTRL_expressions", longName="lookAtSwitch", attributeType="float", defaultValue=0.0, minValue=0.0,
                   maxValue=1.0, keyable=1)
    connectExpression("CTRL_lookAtSwitch", "ty", 0.0, 1.0, 0.0, 1.0, "CTRL_expressions", "lookAtSwitch", 0.0, 1.0)


# ****************************************************************************************************
def customizeJointAppearance():
    jointMapping = {'FACIAL_C_12IPV_AdamsA1': (18, 0.2), 'FACIAL_R_UnderChin': (12, 0.5),
                    'FACIAL_C_LowerLipRotation': (1, 0.7),
                    'FACIAL_C_12IPV_AdamsA2': (18, 0.2), 'FACIAL_C_12IPV_Chin3': (16, 0.1),
                    'FACIAL_C_12IPV_Chin4': (16, 0.1),
                    'FACIAL_C_12IPV_Forehead1': (16, 0.1), 'FACIAL_C_12IPV_Forehead2': (16, 0.1),
                    'FACIAL_C_12IPV_Forehead3': (16, 0.1),
                    'FACIAL_C_12IPV_Forehead4': (16, 0.1), 'FACIAL_C_12IPV_Forehead5': (16, 0.1),
                    'FACIAL_C_12IPV_Forehead6': (16, 0.1),
                    'FACIAL_C_12IPV_LipLowerSkin1': (18, 0.2), 'FACIAL_C_12IPV_LipLowerSkin2': (18, 0.2),
                    'FACIAL_C_12IPV_LipUpperSkin1': (18, 0.2),
                    'FACIAL_C_12IPV_LipUpperSkin2': (18, 0.2), 'FACIAL_C_12IPV_NeckB1': (18, 0.2),
                    'FACIAL_C_12IPV_NeckB2': (18, 0.2),
                    'FACIAL_C_12IPV_NoseBridge1': (18, 0.2), 'FACIAL_C_12IPV_NoseBridge2': (18, 0.2),
                    'FACIAL_C_12IPV_NoseL1': (18, 0.2),
                    'FACIAL_C_12IPV_NoseL2': (18, 0.2), 'FACIAL_C_12IPV_NoseTip1': (16, 0.1),
                    'FACIAL_C_12IPV_NoseTip2': (16, 0.1),
                    'FACIAL_C_12IPV_NoseTip3': (16, 0.1), 'FACIAL_C_12IPV_NoseUpper1': (16, 0.1),
                    'FACIAL_C_12IPV_NoseUpper2': (16, 0.1),
                    'FACIAL_C_AdamsApple': (12, 0.5), 'FACIAL_C_Chin': (12, 1.0), 'FACIAL_C_Chin1': (17, 0.3),
                    'FACIAL_C_Chin2': (17, 0.3), 'FACIAL_C_Chin3': (17, 0.3), 'FACIAL_C_FacialRoot': (1, 0.1),
                    'FACIAL_C_Forehead': (12, 0.6), 'FACIAL_C_Forehead1': (13, 0.3), 'FACIAL_C_Forehead2': (13, 0.3),
                    'FACIAL_C_Forehead3': (13, 0.3), 'FACIAL_C_ForeheadSkin': (14, 0.3), 'FACIAL_C_Hair1': (6, 0.5),
                    'FACIAL_C_Hair2': (6, 0.5), 'FACIAL_C_Hair3': (6, 0.5), 'FACIAL_C_Hair4': (6, 0.5),
                    'FACIAL_C_Hair5': (6, 0.5), 'FACIAL_C_Hair6': (6, 0.5), 'FACIAL_C_Jaw': (1, 0.5),
                    'FACIAL_C_Jawline': (12, 0.5), 'FACIAL_C_LipLower': (12, 0.7), 'FACIAL_C_LipLower1': (17, 0.2),
                    'FACIAL_C_LipLower2': (17, 0.2), 'FACIAL_C_LipLower3': (17, 0.2),
                    'FACIAL_C_LipLowerSkin': (14, 0.3),
                    'FACIAL_C_LipUpper': (12, 0.7), 'FACIAL_C_LipUpper1': (17, 0.2), 'FACIAL_C_LipUpper2': (17, 0.2),
                    'FACIAL_C_LipUpper3': (17, 0.2), 'FACIAL_C_LipUpperSkin': (14, 0.3),
                    'FACIAL_C_MouthLower': (1, 0.2),
                    'FACIAL_C_MouthUpper': (1, 0.2), 'FACIAL_C_Neck1Root': (1, 0.001), 'FACIAL_C_Neck2Root': (1, 0.001),
                    'FACIAL_C_NeckB': (13, 0.3), 'FACIAL_C_Nose': (12, 0.8), 'FACIAL_C_NoseBridge': (12, 0.3),
                    'FACIAL_C_NoseLower': (12, 0.5), 'FACIAL_C_NoseTip': (12, 0.6), 'FACIAL_C_NoseUpper': (17, 0.3),
                    'FACIAL_C_Skull': (1, 2.0), 'FACIAL_C_TeethLower': (17, 0.5), 'FACIAL_C_TeethUpper': (17, 0.5),
                    'FACIAL_C_Tongue1': (6, 0.5), 'FACIAL_C_Tongue2': (6, 0.5), 'FACIAL_C_Tongue3': (6, 0.5),
                    'FACIAL_C_Tongue4': (6, 0.5), 'FACIAL_C_TongueLower3': (6, 0.2), 'FACIAL_C_TongueUpper2': (6, 0.2),
                    'FACIAL_C_TongueUpper3': (6, 0.2), 'FACIAL_C_UnderChin': (12, 0.5),
                    'FACIAL_L_12IPV_CheekL1': (16, 0.1),
                    'FACIAL_L_12IPV_CheekL2': (16, 0.1), 'FACIAL_L_12IPV_CheekL3': (16, 0.1),
                    'FACIAL_L_12IPV_CheekL4': (16, 0.1),
                    'FACIAL_L_12IPV_CheekOuter1': (18, 0.2), 'FACIAL_L_12IPV_CheekOuter2': (18, 0.2),
                    'FACIAL_L_12IPV_CheekOuter3': (18, 0.2),
                    'FACIAL_L_12IPV_CheekOuter4': (18, 0.2), 'FACIAL_L_12IPV_Chin1': (16, 0.1),
                    'FACIAL_L_12IPV_Chin10': (18, 0.2),
                    'FACIAL_L_12IPV_Chin11': (18, 0.2), 'FACIAL_L_12IPV_Chin12': (18, 0.2),
                    'FACIAL_L_12IPV_Chin13': (18, 0.2),
                    'FACIAL_L_12IPV_Chin14': (18, 0.2), 'FACIAL_L_12IPV_Chin2': (16, 0.1),
                    'FACIAL_L_12IPV_Chin5': (18, 0.2),
                    'FACIAL_L_12IPV_Chin6': (18, 0.2), 'FACIAL_L_12IPV_Chin7': (18, 0.2),
                    'FACIAL_L_12IPV_Chin8': (18, 0.2),
                    'FACIAL_L_12IPV_Chin9': (18, 0.2), 'FACIAL_L_12IPV_ChinS1': (16, 0.1),
                    'FACIAL_L_12IPV_ChinS2': (16, 0.1),
                    'FACIAL_L_12IPV_ChinS3': (16, 0.1), 'FACIAL_L_12IPV_ChinS4': (16, 0.1),
                    'FACIAL_L_12IPV_EyeCornerO1': (16, 0.1),
                    'FACIAL_L_12IPV_EyeCornerO2': (16, 0.1), 'FACIAL_L_12IPV_EyesackL1': (18, 0.2),
                    'FACIAL_L_12IPV_EyesackL2': (18, 0.2),
                    'FACIAL_L_12IPV_EyesackL3': (18, 0.2), 'FACIAL_L_12IPV_EyesackL4': (18, 0.2),
                    'FACIAL_L_12IPV_EyesackL5': (18, 0.2),
                    'FACIAL_L_12IPV_EyesackL6': (18, 0.2), 'FACIAL_L_12IPV_EyesackL7': (18, 0.2),
                    'FACIAL_L_12IPV_EyesackL8': (18, 0.2),
                    'FACIAL_L_12IPV_EyesackU0': (16, 0.1), 'FACIAL_L_12IPV_Forehead1': (16, 0.1),
                    'FACIAL_L_12IPV_Forehead2': (16, 0.1),
                    'FACIAL_L_12IPV_Forehead3': (16, 0.1), 'FACIAL_L_12IPV_Forehead4': (16, 0.1),
                    'FACIAL_L_12IPV_Forehead5': (16, 0.1),
                    'FACIAL_L_12IPV_Forehead6': (16, 0.1), 'FACIAL_L_12IPV_ForeheadIn1': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadIn10': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadIn11': (16, 0.1), 'FACIAL_L_12IPV_ForeheadIn12': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadIn13': (18, 0.2),
                    'FACIAL_L_12IPV_ForeheadIn14': (18, 0.2), 'FACIAL_L_12IPV_ForeheadIn2': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadIn3': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadIn4': (16, 0.1), 'FACIAL_L_12IPV_ForeheadIn5': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadIn6': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadIn7': (16, 0.1), 'FACIAL_L_12IPV_ForeheadIn8': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadIn9': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadMid15': (16, 0.1), 'FACIAL_L_12IPV_ForeheadMid16': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadMid17': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadMid18': (16, 0.1), 'FACIAL_L_12IPV_ForeheadMid19': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadMid20': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadMid21': (16, 0.1), 'FACIAL_L_12IPV_ForeheadMid22': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadOut23': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadOut24': (16, 0.1), 'FACIAL_L_12IPV_ForeheadOut25': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadOut26': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadOut27': (16, 0.1), 'FACIAL_L_12IPV_ForeheadOut28': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadOut29': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadOut30': (16, 0.1), 'FACIAL_L_12IPV_ForeheadOut31': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadOut32': (16, 0.1),
                    'FACIAL_L_12IPV_ForeheadSkin1': (18, 0.2), 'FACIAL_L_12IPV_ForeheadSkin2': (18, 0.2),
                    'FACIAL_L_12IPV_ForeheadSkin3': (18, 0.2),
                    'FACIAL_L_12IPV_ForeheadSkin4': (18, 0.2), 'FACIAL_L_12IPV_ForeheadSkin5': (18, 0.2),
                    'FACIAL_L_12IPV_ForeheadSkin6': (18, 0.2),
                    'FACIAL_L_12IPV_Hair1': (16, 0.1), 'FACIAL_L_12IPV_Jawline1': (18, 0.2),
                    'FACIAL_L_12IPV_Jawline2': (18, 0.2),
                    'FACIAL_L_12IPV_Jawline3': (18, 0.2), 'FACIAL_L_12IPV_Jawline4': (18, 0.2),
                    'FACIAL_L_12IPV_Jawline5': (18, 0.2),
                    'FACIAL_L_12IPV_Jawline6': (18, 0.2), 'FACIAL_L_12IPV_LipCorner1': (18, 0.2),
                    'FACIAL_L_12IPV_LipCorner2': (18, 0.2),
                    'FACIAL_L_12IPV_LipCorner3': (18, 0.2), 'FACIAL_L_12IPV_LipLower1': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower10': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower11': (16, 0.1), 'FACIAL_L_12IPV_LipLower12': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower13': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower14': (16, 0.1), 'FACIAL_L_12IPV_LipLower15': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower16': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower17': (16, 0.1), 'FACIAL_L_12IPV_LipLower18': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower19': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower2': (16, 0.1), 'FACIAL_L_12IPV_LipLower20': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower21': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower22': (16, 0.1), 'FACIAL_L_12IPV_LipLower23': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower24': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower3': (16, 0.1), 'FACIAL_L_12IPV_LipLower4': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower5': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower6': (16, 0.1), 'FACIAL_L_12IPV_LipLower7': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower8': (16, 0.1),
                    'FACIAL_L_12IPV_LipLower9': (16, 0.1), 'FACIAL_L_12IPV_LipLowerOuterSkin1': (18, 0.2),
                    'FACIAL_L_12IPV_LipLowerOuterSkin2': (18, 0.2),
                    'FACIAL_L_12IPV_LipLowerOuterSkin3': (18, 0.2), 'FACIAL_L_12IPV_LipLowerSkin': (18, 0.2),
                    'FACIAL_L_12IPV_LipUpper1': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper10': (16, 0.1), 'FACIAL_L_12IPV_LipUpper11': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper12': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper13': (16, 0.1), 'FACIAL_L_12IPV_LipUpper14': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper15': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper16': (16, 0.1), 'FACIAL_L_12IPV_LipUpper17': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper18': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper19': (16, 0.1), 'FACIAL_L_12IPV_LipUpper2': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper20': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper21': (16, 0.1), 'FACIAL_L_12IPV_LipUpper22': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper23': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper24': (16, 0.1), 'FACIAL_L_12IPV_LipUpper3': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper4': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper5': (16, 0.1), 'FACIAL_L_12IPV_LipUpper6': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper7': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpper8': (16, 0.1), 'FACIAL_L_12IPV_LipUpper9': (16, 0.1),
                    'FACIAL_L_12IPV_LipUpperOuterSkin1': (18, 0.2),
                    'FACIAL_L_12IPV_LipUpperOuterSkin2': (18, 0.2), 'FACIAL_L_12IPV_LipUpperSkin': (18, 0.2),
                    'FACIAL_L_12IPV_MouthInteriorLower1': (18, 0.2),
                    'FACIAL_L_12IPV_MouthInteriorLower2': (18, 0.2), 'FACIAL_L_12IPV_MouthInteriorUpper1': (18, 0.2),
                    'FACIAL_L_12IPV_MouthInteriorUpper2': (18, 0.2),
                    'FACIAL_L_12IPV_NasolabialB1': (18, 0.2), 'FACIAL_L_12IPV_NasolabialB10': (18, 0.2),
                    'FACIAL_L_12IPV_NasolabialB11': (18, 0.2),
                    'FACIAL_L_12IPV_NasolabialB12': (18, 0.2), 'FACIAL_L_12IPV_NasolabialB13': (18, 0.2),
                    'FACIAL_L_12IPV_NasolabialB14': (18, 0.2),
                    'FACIAL_L_12IPV_NasolabialB15': (18, 0.2), 'FACIAL_L_12IPV_NasolabialB2': (18, 0.2),
                    'FACIAL_L_12IPV_NasolabialB3': (18, 0.2),
                    'FACIAL_L_12IPV_NasolabialB4': (18, 0.2), 'FACIAL_L_12IPV_NasolabialB5': (18, 0.2),
                    'FACIAL_L_12IPV_NasolabialB6': (18, 0.2),
                    'FACIAL_L_12IPV_NasolabialB7': (18, 0.2), 'FACIAL_L_12IPV_NasolabialB8': (18, 0.2),
                    'FACIAL_L_12IPV_NasolabialB9': (18, 0.2),
                    'FACIAL_L_12IPV_NasolabialF1': (16, 0.1), 'FACIAL_L_12IPV_NasolabialF2': (16, 0.1),
                    'FACIAL_L_12IPV_NasolabialF3': (16, 0.1),
                    'FACIAL_L_12IPV_NasolabialF4': (16, 0.1), 'FACIAL_L_12IPV_NasolabialF5': (16, 0.1),
                    'FACIAL_L_12IPV_NasolabialF6': (16, 0.1),
                    'FACIAL_L_12IPV_NasolabialF7': (16, 0.1), 'FACIAL_L_12IPV_NasolabialF8': (16, 0.1),
                    'FACIAL_L_12IPV_NasolabialF9': (16, 0.1),
                    'FACIAL_L_12IPV_NeckA1': (18, 0.2), 'FACIAL_L_12IPV_NeckA2': (18, 0.2),
                    'FACIAL_L_12IPV_NeckA3': (18, 0.2),
                    'FACIAL_L_12IPV_NeckA4': (18, 0.2), 'FACIAL_L_12IPV_NeckA5': (18, 0.2),
                    'FACIAL_L_12IPV_NeckA6': (18, 0.2),
                    'FACIAL_L_12IPV_NeckA7': (18, 0.2), 'FACIAL_L_12IPV_NeckA8': (18, 0.2),
                    'FACIAL_L_12IPV_NeckA9': (18, 0.2),
                    'FACIAL_L_12IPV_NeckB3': (18, 0.2), 'FACIAL_L_12IPV_NeckB4': (18, 0.2),
                    'FACIAL_L_12IPV_NeckB5': (18, 0.2),
                    'FACIAL_L_12IPV_NeckB6': (18, 0.2), 'FACIAL_L_12IPV_NeckB7': (18, 0.2),
                    'FACIAL_L_12IPV_NeckB8': (18, 0.2),
                    'FACIAL_L_12IPV_NoseBridge1': (18, 0.2), 'FACIAL_L_12IPV_NoseBridge2': (18, 0.2),
                    'FACIAL_L_12IPV_NoseTip1': (16, 0.1),
                    'FACIAL_L_12IPV_NoseTip2': (16, 0.1), 'FACIAL_L_12IPV_NoseTip3': (16, 0.1),
                    'FACIAL_L_12IPV_NoseUpper1': (16, 0.1),
                    'FACIAL_L_12IPV_NoseUpper2': (16, 0.1), 'FACIAL_L_12IPV_NoseUpper3': (16, 0.1),
                    'FACIAL_L_12IPV_NoseUpper4': (16, 0.1),
                    'FACIAL_L_12IPV_NoseUpper5': (16, 0.1), 'FACIAL_L_12IPV_NoseUpper6': (16, 0.1),
                    'FACIAL_L_12IPV_Nostril1': (18, 0.2),
                    'FACIAL_L_12IPV_Nostril10': (18, 0.2), 'FACIAL_L_12IPV_Nostril11': (18, 0.2),
                    'FACIAL_L_12IPV_Nostril12': (18, 0.2),
                    'FACIAL_L_12IPV_Nostril13': (18, 0.2), 'FACIAL_L_12IPV_Nostril14': (18, 0.2),
                    'FACIAL_L_12IPV_Nostril2': (18, 0.2),
                    'FACIAL_L_12IPV_Nostril3': (18, 0.2), 'FACIAL_L_12IPV_Nostril4': (18, 0.2),
                    'FACIAL_L_12IPV_Nostril5': (18, 0.2),
                    'FACIAL_L_12IPV_Nostril6': (18, 0.2), 'FACIAL_L_12IPV_Nostril7': (18, 0.2),
                    'FACIAL_L_12IPV_Nostril8': (18, 0.2),
                    'FACIAL_L_12IPV_Nostril9': (18, 0.2), 'FACIAL_L_12IPV_Temple1': (18, 0.2),
                    'FACIAL_L_12IPV_Temple2': (18, 0.2),
                    'FACIAL_L_12IPV_Temple3': (18, 0.2), 'FACIAL_L_12IPV_Temple4': (18, 0.2),
                    'FACIAL_L_12IPV_UnderChin1': (16, 0.1),
                    'FACIAL_L_12IPV_UnderChin2': (16, 0.1), 'FACIAL_L_12IPV_UnderChin3': (16, 0.1),
                    'FACIAL_L_12IPV_UnderChin4': (16, 0.1),
                    'FACIAL_L_12IPV_UnderChin5': (16, 0.1), 'FACIAL_L_12IPV_UnderChin6': (16, 0.1),
                    'FACIAL_L_CheekInner': (12, 0.8),
                    'FACIAL_L_CheekInner1': (13, 0.3), 'FACIAL_L_CheekInner2': (13, 0.3),
                    'FACIAL_L_CheekInner3': (13, 0.3),
                    'FACIAL_L_CheekInner4': (13, 0.3), 'FACIAL_L_CheekLower': (12, 1.0),
                    'FACIAL_L_CheekLower1': (17, 0.3),
                    'FACIAL_L_CheekLower2': (17, 0.3), 'FACIAL_L_CheekOuter': (12, 1.0),
                    'FACIAL_L_CheekOuter1': (17, 0.3),
                    'FACIAL_L_CheekOuter2': (17, 0.3), 'FACIAL_L_CheekOuter3': (17, 0.3),
                    'FACIAL_L_CheekOuter4': (13, 0.3),
                    'FACIAL_L_Chin1': (17, 0.3), 'FACIAL_L_Chin2': (17, 0.3), 'FACIAL_L_Chin3': (17, 0.3),
                    'FACIAL_L_ChinSide': (12, 0.5), 'FACIAL_L_Ear': (12, 1.0), 'FACIAL_L_Ear1': (17, 0.5),
                    'FACIAL_L_Ear2': (17, 0.5), 'FACIAL_L_Ear3': (17, 0.5), 'FACIAL_L_Ear4': (17, 0.5),
                    'FACIAL_L_Eye': (6, 1.5), 'FACIAL_L_EyeCornerInner': (12, 0.2),
                    'FACIAL_L_EyeCornerInner1': (17, 0.1),
                    'FACIAL_L_EyeCornerInner2': (17, 0.1), 'FACIAL_L_EyeCornerOuter': (12, 0.2),
                    'FACIAL_L_EyeCornerOuter1': (17, 0.1),
                    'FACIAL_L_EyeCornerOuter2': (17, 0.1), 'FACIAL_L_EyeParallel': (6, 0.8),
                    'FACIAL_L_EyelashesCornerOuter1': (16, 0.03),
                    'FACIAL_L_EyelashesUpperA1': (16, 0.03), 'FACIAL_L_EyelashesUpperA2': (16, 0.03),
                    'FACIAL_L_EyelashesUpperA3': (16, 0.03),
                    'FACIAL_L_EyelidLowerA': (12, 0.6), 'FACIAL_L_EyelidLowerA1': (13, 0.1),
                    'FACIAL_L_EyelidLowerA2': (13, 0.1),
                    'FACIAL_L_EyelidLowerA3': (13, 0.1), 'FACIAL_L_EyelidLowerB': (12, 0.6),
                    'FACIAL_L_EyelidLowerB1': (13, 0.1),
                    'FACIAL_L_EyelidLowerB2': (13, 0.1), 'FACIAL_L_EyelidLowerB3': (13, 0.1),
                    'FACIAL_L_EyelidUpperA': (12, 0.6),
                    'FACIAL_L_EyelidUpperA1': (13, 0.1), 'FACIAL_L_EyelidUpperA2': (13, 0.1),
                    'FACIAL_L_EyelidUpperA3': (13, 0.1),
                    'FACIAL_L_EyelidUpperB': (12, 0.6), 'FACIAL_L_EyelidUpperB1': (13, 0.1),
                    'FACIAL_L_EyelidUpperB2': (13, 0.1),
                    'FACIAL_L_EyelidUpperB3': (13, 0.1), 'FACIAL_L_EyelidUpperFurrow': (12, 0.2),
                    'FACIAL_L_EyelidUpperFurrow1': (17, 0.1),
                    'FACIAL_L_EyelidUpperFurrow2': (17, 0.1), 'FACIAL_L_EyelidUpperFurrow3': (17, 0.1),
                    'FACIAL_L_EyesackLower': (12, 0.4),
                    'FACIAL_L_EyesackLower1': (17, 0.3), 'FACIAL_L_EyesackLower2': (17, 0.3),
                    'FACIAL_L_EyesackUpper': (12, 0.3),
                    'FACIAL_L_EyesackUpper1': (14, 0.2), 'FACIAL_L_EyesackUpper2': (14, 0.2),
                    'FACIAL_L_EyesackUpper3': (14, 0.2),
                    'FACIAL_L_EyesackUpper4': (14, 0.2), 'FACIAL_L_Forehead1': (13, 0.3),
                    'FACIAL_L_Forehead2': (13, 0.3),
                    'FACIAL_L_Forehead3': (13, 0.3), 'FACIAL_L_ForeheadIn': (12, 0.6),
                    'FACIAL_L_ForeheadInA1': (17, 0.3),
                    'FACIAL_L_ForeheadInA2': (17, 0.3), 'FACIAL_L_ForeheadInA3': (17, 0.3),
                    'FACIAL_L_ForeheadInB1': (17, 0.3),
                    'FACIAL_L_ForeheadInB2': (17, 0.3), 'FACIAL_L_ForeheadInSkin': (14, 0.3),
                    'FACIAL_L_ForeheadMid': (12, 0.6),
                    'FACIAL_L_ForeheadMid1': (17, 0.3), 'FACIAL_L_ForeheadMid2': (17, 0.3),
                    'FACIAL_L_ForeheadMidSkin': (14, 0.3),
                    'FACIAL_L_ForeheadOut': (12, 0.6), 'FACIAL_L_ForeheadOutA1': (17, 0.3),
                    'FACIAL_L_ForeheadOutA2': (17, 0.3),
                    'FACIAL_L_ForeheadOutB1': (17, 0.3), 'FACIAL_L_ForeheadOutB2': (17, 0.3),
                    'FACIAL_L_ForeheadOutSkin': (14, 0.3),
                    'FACIAL_L_HairA1': (6, 0.5), 'FACIAL_L_HairA2': (6, 0.5), 'FACIAL_L_HairA3': (6, 0.5),
                    'FACIAL_L_HairA4': (6, 0.5), 'FACIAL_L_HairA5': (6, 0.5), 'FACIAL_L_HairA6': (6, 0.5),
                    'FACIAL_L_HairB1': (6, 0.5), 'FACIAL_L_HairB2': (6, 0.5), 'FACIAL_L_HairB3': (6, 0.5),
                    'FACIAL_L_HairB4': (6, 0.5), 'FACIAL_L_HairB5': (6, 0.5), 'FACIAL_L_HairC1': (6, 0.5),
                    'FACIAL_L_HairC2': (6, 0.5), 'FACIAL_L_HairC3': (6, 0.5), 'FACIAL_L_HairC4': (6, 0.5),
                    'FACIAL_L_JawBulge': (17, 0.5), 'FACIAL_L_JawRecess': (17, 0.5), 'FACIAL_L_Jawline': (12, 0.5),
                    'FACIAL_L_Jawline1': (13, 0.3), 'FACIAL_L_Jawline2': (13, 0.3), 'FACIAL_L_LipCorner': (12, 0.7),
                    'FACIAL_L_LipCorner1': (13, 0.2), 'FACIAL_L_LipCorner2': (13, 0.2),
                    'FACIAL_L_LipCorner3': (13, 0.2),
                    'FACIAL_L_LipLower': (12, 0.7), 'FACIAL_L_LipLower1': (17, 0.2), 'FACIAL_L_LipLower2': (17, 0.2),
                    'FACIAL_L_LipLower3': (17, 0.2), 'FACIAL_L_LipLowerOuter': (12, 0.7),
                    'FACIAL_L_LipLowerOuter1': (17, 0.2),
                    'FACIAL_L_LipLowerOuter2': (17, 0.2), 'FACIAL_L_LipLowerOuter3': (17, 0.2),
                    'FACIAL_L_LipLowerOuterSkin': (14, 0.3),
                    'FACIAL_L_LipLowerSkin': (14, 0.3), 'FACIAL_L_LipUpper': (12, 0.7), 'FACIAL_L_LipUpper1': (17, 0.2),
                    'FACIAL_L_LipUpper2': (17, 0.2), 'FACIAL_L_LipUpper3': (17, 0.2),
                    'FACIAL_L_LipUpperOuter': (12, 0.7),
                    'FACIAL_L_LipUpperOuter1': (17, 0.2), 'FACIAL_L_LipUpperOuter2': (17, 0.2),
                    'FACIAL_L_LipUpperOuter3': (17, 0.2),
                    'FACIAL_L_LipUpperOuterSkin': (14, 0.3), 'FACIAL_L_LipUpperSkin': (14, 0.3),
                    'FACIAL_L_Masseter': (12, 1.0),
                    'FACIAL_L_NasolabialBulge': (12, 0.6), 'FACIAL_L_NasolabialBulge1': (14, 0.4),
                    'FACIAL_L_NasolabialBulge2': (14, 0.4),
                    'FACIAL_L_NasolabialBulge3': (14, 0.4), 'FACIAL_L_NasolabialFurrow': (12, 0.5),
                    'FACIAL_L_NeckA1': (13, 0.3),
                    'FACIAL_L_NeckA2': (13, 0.3), 'FACIAL_L_NeckA3': (13, 0.3), 'FACIAL_L_NeckA4': (13, 0.3),
                    'FACIAL_L_NeckB1': (13, 0.3), 'FACIAL_L_NeckB2': (13, 0.3), 'FACIAL_L_NeckB3': (13, 0.3),
                    'FACIAL_L_NeckB4': (13, 0.3), 'FACIAL_L_NoseBridge': (13, 0.3), 'FACIAL_L_NoseUpper': (17, 0.3),
                    'FACIAL_L_Nostril': (12, 0.8), 'FACIAL_L_NostrilThickness1': (17, 0.2),
                    'FACIAL_L_NostrilThickness2': (17, 0.2),
                    'FACIAL_L_NostrilThickness3': (17, 0.2), 'FACIAL_L_Pupil': (6, 0.6), 'FACIAL_L_Sideburn1': (6, 0.5),
                    'FACIAL_L_Sideburn2': (6, 0.5), 'FACIAL_L_Sideburn3': (6, 0.5), 'FACIAL_L_Sideburn4': (6, 0.5),
                    'FACIAL_L_Sideburn5': (6, 0.5), 'FACIAL_L_Sideburn6': (6, 0.5), 'FACIAL_L_Temple': (17, 0.5),
                    'FACIAL_L_TongueSide2': (6, 0.2), 'FACIAL_L_TongueSide3': (6, 0.2), 'FACIAL_L_UnderChin': (12, 0.5),
                    'FACIAL_R_12IPV_CheekL1': (16, 0.1), 'FACIAL_R_12IPV_CheekL2': (16, 0.1),
                    'FACIAL_R_12IPV_CheekL3': (16, 0.1),
                    'FACIAL_R_12IPV_CheekL4': (16, 0.1), 'FACIAL_R_12IPV_CheekOuter1': (18, 0.2),
                    'FACIAL_R_12IPV_CheekOuter2': (18, 0.2),
                    'FACIAL_R_12IPV_CheekOuter3': (18, 0.2), 'FACIAL_R_12IPV_CheekOuter4': (18, 0.2),
                    'FACIAL_R_12IPV_Chin1': (16, 0.1),
                    'FACIAL_R_12IPV_Chin10': (18, 0.2), 'FACIAL_R_12IPV_Chin11': (18, 0.2),
                    'FACIAL_R_12IPV_Chin12': (18, 0.2),
                    'FACIAL_R_12IPV_Chin13': (18, 0.2), 'FACIAL_R_12IPV_Chin14': (18, 0.2),
                    'FACIAL_R_12IPV_Chin2': (16, 0.1),
                    'FACIAL_R_12IPV_Chin5': (18, 0.2), 'FACIAL_R_12IPV_Chin6': (18, 0.2),
                    'FACIAL_R_12IPV_Chin7': (18, 0.2),
                    'FACIAL_R_12IPV_Chin8': (18, 0.2), 'FACIAL_R_12IPV_Chin9': (18, 0.2),
                    'FACIAL_R_12IPV_ChinS1': (16, 0.1),
                    'FACIAL_R_12IPV_ChinS2': (16, 0.1), 'FACIAL_R_12IPV_ChinS3': (16, 0.1),
                    'FACIAL_R_12IPV_ChinS4': (16, 0.1),
                    'FACIAL_R_12IPV_EyeCornerO1': (16, 0.1), 'FACIAL_R_12IPV_EyeCornerO2': (16, 0.1),
                    'FACIAL_R_12IPV_EyesackL1': (18, 0.2),
                    'FACIAL_R_12IPV_EyesackL2': (18, 0.2), 'FACIAL_R_12IPV_EyesackL3': (18, 0.2),
                    'FACIAL_R_12IPV_EyesackL4': (18, 0.2),
                    'FACIAL_R_12IPV_EyesackL5': (18, 0.2), 'FACIAL_R_12IPV_EyesackL6': (18, 0.2),
                    'FACIAL_R_12IPV_EyesackL7': (18, 0.2),
                    'FACIAL_R_12IPV_EyesackL8': (18, 0.2), 'FACIAL_R_12IPV_EyesackU0': (16, 0.1),
                    'FACIAL_R_12IPV_Forehead1': (16, 0.1),
                    'FACIAL_R_12IPV_Forehead2': (16, 0.1), 'FACIAL_R_12IPV_Forehead3': (16, 0.1),
                    'FACIAL_R_12IPV_Forehead4': (16, 0.1),
                    'FACIAL_R_12IPV_Forehead5': (16, 0.1), 'FACIAL_R_12IPV_Forehead6': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadIn1': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadIn10': (16, 0.1), 'FACIAL_R_12IPV_ForeheadIn11': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadIn12': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadIn13': (18, 0.2), 'FACIAL_R_12IPV_ForeheadIn14': (18, 0.2),
                    'FACIAL_R_12IPV_ForeheadIn2': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadIn3': (16, 0.1), 'FACIAL_R_12IPV_ForeheadIn4': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadIn5': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadIn6': (16, 0.1), 'FACIAL_R_12IPV_ForeheadIn7': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadIn8': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadIn9': (16, 0.1), 'FACIAL_R_12IPV_ForeheadMid15': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadMid16': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadMid17': (16, 0.1), 'FACIAL_R_12IPV_ForeheadMid18': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadMid19': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadMid20': (16, 0.1), 'FACIAL_R_12IPV_ForeheadMid21': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadMid22': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadOut23': (16, 0.1), 'FACIAL_R_12IPV_ForeheadOut24': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadOut25': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadOut26': (16, 0.1), 'FACIAL_R_12IPV_ForeheadOut27': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadOut28': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadOut29': (16, 0.1), 'FACIAL_R_12IPV_ForeheadOut30': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadOut31': (16, 0.1),
                    'FACIAL_R_12IPV_ForeheadOut32': (16, 0.1), 'FACIAL_R_12IPV_ForeheadSkin1': (18, 0.2),
                    'FACIAL_R_12IPV_ForeheadSkin2': (18, 0.2),
                    'FACIAL_R_12IPV_ForeheadSkin3': (18, 0.2), 'FACIAL_R_12IPV_ForeheadSkin4': (18, 0.2),
                    'FACIAL_R_12IPV_ForeheadSkin5': (18, 0.2),
                    'FACIAL_R_12IPV_ForeheadSkin6': (18, 0.2), 'FACIAL_R_12IPV_Hair1': (16, 0.1),
                    'FACIAL_R_12IPV_Jawline1': (18, 0.2),
                    'FACIAL_R_12IPV_Jawline2': (18, 0.2), 'FACIAL_R_12IPV_Jawline3': (18, 0.2),
                    'FACIAL_R_12IPV_Jawline4': (18, 0.2),
                    'FACIAL_R_12IPV_Jawline5': (18, 0.2), 'FACIAL_R_12IPV_Jawline6': (18, 0.2),
                    'FACIAL_R_12IPV_LipCorner1': (18, 0.2),
                    'FACIAL_R_12IPV_LipCorner2': (18, 0.2), 'FACIAL_R_12IPV_LipCorner3': (18, 0.2),
                    'FACIAL_R_12IPV_LipLower1': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower10': (16, 0.1), 'FACIAL_R_12IPV_LipLower11': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower12': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower13': (16, 0.1), 'FACIAL_R_12IPV_LipLower14': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower15': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower16': (16, 0.1), 'FACIAL_R_12IPV_LipLower17': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower18': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower19': (16, 0.1), 'FACIAL_R_12IPV_LipLower2': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower20': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower21': (16, 0.1), 'FACIAL_R_12IPV_LipLower22': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower23': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower24': (16, 0.1), 'FACIAL_R_12IPV_LipLower3': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower4': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower5': (16, 0.1), 'FACIAL_R_12IPV_LipLower6': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower7': (16, 0.1),
                    'FACIAL_R_12IPV_LipLower8': (16, 0.1), 'FACIAL_R_12IPV_LipLower9': (16, 0.1),
                    'FACIAL_R_12IPV_LipLowerOuterSkin1': (18, 0.2),
                    'FACIAL_R_12IPV_LipLowerOuterSkin2': (18, 0.2), 'FACIAL_R_12IPV_LipLowerOuterSkin3': (18, 0.2),
                    'FACIAL_R_12IPV_LipLowerSkin': (18, 0.2),
                    'FACIAL_R_12IPV_LipUpper1': (16, 0.1), 'FACIAL_R_12IPV_LipUpper10': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper11': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper12': (16, 0.1), 'FACIAL_R_12IPV_LipUpper13': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper14': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper15': (16, 0.1), 'FACIAL_R_12IPV_LipUpper16': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper17': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper18': (16, 0.1), 'FACIAL_R_12IPV_LipUpper19': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper2': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper20': (16, 0.1), 'FACIAL_R_12IPV_LipUpper21': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper22': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper23': (16, 0.1), 'FACIAL_R_12IPV_LipUpper24': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper3': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper4': (16, 0.1), 'FACIAL_R_12IPV_LipUpper5': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper6': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper7': (16, 0.1), 'FACIAL_R_12IPV_LipUpper8': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpper9': (16, 0.1),
                    'FACIAL_R_12IPV_LipUpperOuterSkin1': (18, 0.2), 'FACIAL_R_12IPV_LipUpperOuterSkin2': (18, 0.2),
                    'FACIAL_R_12IPV_LipUpperSkin': (18, 0.2),
                    'FACIAL_R_12IPV_MouthInteriorLower1': (18, 0.2), 'FACIAL_R_12IPV_MouthInteriorLower2': (18, 0.2),
                    'FACIAL_R_12IPV_MouthInteriorUpper1': (18, 0.2),
                    'FACIAL_R_12IPV_MouthInteriorUpper2': (18, 0.2), 'FACIAL_R_12IPV_NasolabialB1': (18, 0.2),
                    'FACIAL_R_12IPV_NasolabialB10': (18, 0.2),
                    'FACIAL_R_12IPV_NasolabialB11': (18, 0.2), 'FACIAL_R_12IPV_NasolabialB12': (18, 0.2),
                    'FACIAL_R_12IPV_NasolabialB13': (18, 0.2),
                    'FACIAL_R_12IPV_NasolabialB14': (18, 0.2), 'FACIAL_R_12IPV_NasolabialB15': (18, 0.2),
                    'FACIAL_R_12IPV_NasolabialB2': (18, 0.2),
                    'FACIAL_R_12IPV_NasolabialB3': (18, 0.2), 'FACIAL_R_12IPV_NasolabialB4': (18, 0.2),
                    'FACIAL_R_12IPV_NasolabialB5': (18, 0.2),
                    'FACIAL_R_12IPV_NasolabialB6': (18, 0.2), 'FACIAL_R_12IPV_NasolabialB7': (18, 0.2),
                    'FACIAL_R_12IPV_NasolabialB8': (18, 0.2),
                    'FACIAL_R_12IPV_NasolabialB9': (18, 0.2), 'FACIAL_R_12IPV_NasolabialF1': (16, 0.1),
                    'FACIAL_R_12IPV_NasolabialF2': (16, 0.1),
                    'FACIAL_R_12IPV_NasolabialF3': (16, 0.1), 'FACIAL_R_12IPV_NasolabialF4': (16, 0.1),
                    'FACIAL_R_12IPV_NasolabialF5': (16, 0.1),
                    'FACIAL_R_12IPV_NasolabialF6': (16, 0.1), 'FACIAL_R_12IPV_NasolabialF7': (16, 0.1),
                    'FACIAL_R_12IPV_NasolabialF8': (16, 0.1),
                    'FACIAL_R_12IPV_NasolabialF9': (16, 0.1), 'FACIAL_R_12IPV_NeckA1': (18, 0.2),
                    'FACIAL_R_12IPV_NeckA2': (18, 0.2),
                    'FACIAL_R_12IPV_NeckA3': (18, 0.2), 'FACIAL_R_12IPV_NeckA4': (18, 0.2),
                    'FACIAL_R_12IPV_NeckA5': (18, 0.2),
                    'FACIAL_R_12IPV_NeckA6': (18, 0.2), 'FACIAL_R_12IPV_NeckA7': (18, 0.2),
                    'FACIAL_R_12IPV_NeckA8': (18, 0.2),
                    'FACIAL_R_12IPV_NeckA9': (18, 0.2), 'FACIAL_R_12IPV_NeckB3': (18, 0.2),
                    'FACIAL_R_12IPV_NeckB4': (18, 0.2),
                    'FACIAL_R_12IPV_NeckB5': (18, 0.2), 'FACIAL_R_12IPV_NeckB6': (18, 0.2),
                    'FACIAL_R_12IPV_NeckB7': (18, 0.2),
                    'FACIAL_R_12IPV_NeckB8': (18, 0.2), 'FACIAL_R_12IPV_NoseBridge1': (18, 0.2),
                    'FACIAL_R_12IPV_NoseBridge2': (18, 0.2),
                    'FACIAL_R_12IPV_NoseTip1': (16, 0.1), 'FACIAL_R_12IPV_NoseTip2': (16, 0.1),
                    'FACIAL_R_12IPV_NoseTip3': (16, 0.1),
                    'FACIAL_R_12IPV_NoseUpper1': (16, 0.1), 'FACIAL_R_12IPV_NoseUpper2': (16, 0.1),
                    'FACIAL_R_12IPV_NoseUpper3': (16, 0.1),
                    'FACIAL_R_12IPV_NoseUpper4': (16, 0.1), 'FACIAL_R_12IPV_NoseUpper5': (16, 0.1),
                    'FACIAL_R_12IPV_NoseUpper6': (16, 0.1),
                    'FACIAL_R_12IPV_Nostril1': (18, 0.2), 'FACIAL_R_12IPV_Nostril10': (18, 0.2),
                    'FACIAL_R_12IPV_Nostril11': (18, 0.2),
                    'FACIAL_R_12IPV_Nostril12': (18, 0.2), 'FACIAL_R_12IPV_Nostril13': (18, 0.2),
                    'FACIAL_R_12IPV_Nostril14': (18, 0.2),
                    'FACIAL_R_12IPV_Nostril2': (18, 0.2), 'FACIAL_R_12IPV_Nostril3': (18, 0.2),
                    'FACIAL_R_12IPV_Nostril4': (18, 0.2),
                    'FACIAL_R_12IPV_Nostril5': (18, 0.2), 'FACIAL_R_12IPV_Nostril6': (18, 0.2),
                    'FACIAL_R_12IPV_Nostril7': (18, 0.2),
                    'FACIAL_R_12IPV_Nostril8': (18, 0.2), 'FACIAL_R_12IPV_Nostril9': (18, 0.2),
                    'FACIAL_R_12IPV_Temple1': (18, 0.2),
                    'FACIAL_R_12IPV_Temple2': (18, 0.2), 'FACIAL_R_12IPV_Temple3': (18, 0.2),
                    'FACIAL_R_12IPV_Temple4': (18, 0.2),
                    'FACIAL_R_12IPV_UnderChin1': (16, 0.1), 'FACIAL_R_12IPV_UnderChin2': (16, 0.1),
                    'FACIAL_R_12IPV_UnderChin3': (16, 0.1),
                    'FACIAL_R_12IPV_UnderChin4': (16, 0.1), 'FACIAL_R_12IPV_UnderChin5': (16, 0.1),
                    'FACIAL_R_12IPV_UnderChin6': (16, 0.1),
                    'FACIAL_R_CheekInner': (12, 0.8), 'FACIAL_R_CheekInner1': (13, 0.3),
                    'FACIAL_R_CheekInner2': (13, 0.3),
                    'FACIAL_R_CheekInner3': (13, 0.3), 'FACIAL_R_CheekInner4': (13, 0.3),
                    'FACIAL_R_CheekLower': (12, 1.0),
                    'FACIAL_R_CheekLower1': (17, 0.3), 'FACIAL_R_CheekLower2': (17, 0.3),
                    'FACIAL_R_CheekOuter': (12, 1.0),
                    'FACIAL_R_CheekOuter1': (17, 0.3), 'FACIAL_R_CheekOuter2': (17, 0.3),
                    'FACIAL_R_CheekOuter3': (17, 0.3),
                    'FACIAL_R_CheekOuter4': (13, 0.3), 'FACIAL_R_Chin1': (17, 0.3), 'FACIAL_R_Chin2': (17, 0.3),
                    'FACIAL_R_Chin3': (17, 0.3), 'FACIAL_R_ChinSide': (12, 0.5), 'FACIAL_R_Ear': (12, 1.0),
                    'FACIAL_R_Ear1': (17, 0.5), 'FACIAL_R_Ear2': (17, 0.5), 'FACIAL_R_Ear3': (17, 0.5),
                    'FACIAL_R_Ear4': (17, 0.5), 'FACIAL_R_Eye': (6, 1.5), 'FACIAL_R_EyeCornerInner': (12, 0.2),
                    'FACIAL_R_EyeCornerInner1': (17, 0.1), 'FACIAL_R_EyeCornerInner2': (17, 0.1),
                    'FACIAL_R_EyeCornerOuter': (12, 0.2),
                    'FACIAL_R_EyeCornerOuter1': (17, 0.1), 'FACIAL_R_EyeCornerOuter2': (17, 0.1),
                    'FACIAL_R_EyeParallel': (6, 0.8),
                    'FACIAL_R_EyelashesCornerOuter1': (16, 0.03), 'FACIAL_R_EyelashesUpperA1': (16, 0.03),
                    'FACIAL_R_EyelashesUpperA2': (16, 0.03),
                    'FACIAL_R_EyelashesUpperA3': (16, 0.03), 'FACIAL_R_EyelidLowerA': (12, 0.6),
                    'FACIAL_R_EyelidLowerA1': (13, 0.1),
                    'FACIAL_R_EyelidLowerA2': (13, 0.1), 'FACIAL_R_EyelidLowerA3': (13, 0.1),
                    'FACIAL_R_EyelidLowerB': (12, 0.6),
                    'FACIAL_R_EyelidLowerB1': (13, 0.1), 'FACIAL_R_EyelidLowerB2': (13, 0.1),
                    'FACIAL_R_EyelidLowerB3': (13, 0.1),
                    'FACIAL_R_EyelidUpperA': (12, 0.6), 'FACIAL_R_EyelidUpperA1': (13, 0.1),
                    'FACIAL_R_EyelidUpperA2': (13, 0.1),
                    'FACIAL_R_EyelidUpperA3': (13, 0.1), 'FACIAL_R_EyelidUpperB': (12, 0.6),
                    'FACIAL_R_EyelidUpperB1': (13, 0.1),
                    'FACIAL_R_EyelidUpperB2': (13, 0.1), 'FACIAL_R_EyelidUpperB3': (13, 0.1),
                    'FACIAL_R_EyelidUpperFurrow': (12, 0.2),
                    'FACIAL_R_EyelidUpperFurrow1': (17, 0.1), 'FACIAL_R_EyelidUpperFurrow2': (17, 0.1),
                    'FACIAL_R_EyelidUpperFurrow3': (17, 0.1),
                    'FACIAL_R_EyesackLower': (12, 0.4), 'FACIAL_R_EyesackLower1': (17, 0.3),
                    'FACIAL_R_EyesackLower2': (17, 0.3),
                    'FACIAL_R_EyesackUpper': (12, 0.3), 'FACIAL_R_EyesackUpper1': (14, 0.2),
                    'FACIAL_R_EyesackUpper2': (14, 0.2),
                    'FACIAL_R_EyesackUpper3': (14, 0.2), 'FACIAL_R_EyesackUpper4': (14, 0.2),
                    'FACIAL_R_Forehead1': (13, 0.3),
                    'FACIAL_R_Forehead2': (13, 0.3), 'FACIAL_R_Forehead3': (13, 0.3), 'FACIAL_R_ForeheadIn': (12, 0.6),
                    'FACIAL_R_ForeheadInA1': (17, 0.3), 'FACIAL_R_ForeheadInA2': (17, 0.3),
                    'FACIAL_R_ForeheadInA3': (17, 0.3),
                    'FACIAL_R_ForeheadInB1': (17, 0.3), 'FACIAL_R_ForeheadInB2': (17, 0.3),
                    'FACIAL_R_ForeheadInSkin': (14, 0.3),
                    'FACIAL_R_ForeheadMid': (12, 0.6), 'FACIAL_R_ForeheadMid1': (17, 0.3),
                    'FACIAL_R_ForeheadMid2': (17, 0.3),
                    'FACIAL_R_ForeheadMidSkin': (14, 0.3), 'FACIAL_R_ForeheadOut': (12, 0.6),
                    'FACIAL_R_ForeheadOutA1': (17, 0.3),
                    'FACIAL_R_ForeheadOutA2': (17, 0.3), 'FACIAL_R_ForeheadOutB1': (17, 0.3),
                    'FACIAL_R_ForeheadOutB2': (17, 0.3),
                    'FACIAL_R_ForeheadOutSkin': (14, 0.3), 'FACIAL_R_HairA1': (6, 0.5), 'FACIAL_R_HairA2': (6, 0.5),
                    'FACIAL_R_HairA3': (6, 0.5), 'FACIAL_R_HairA4': (6, 0.5), 'FACIAL_R_HairA5': (6, 0.5),
                    'FACIAL_R_HairA6': (6, 0.5), 'FACIAL_R_HairB1': (6, 0.5), 'FACIAL_R_HairB2': (6, 0.5),
                    'FACIAL_R_HairB3': (6, 0.5), 'FACIAL_R_HairB4': (6, 0.5), 'FACIAL_R_HairB5': (6, 0.5),
                    'FACIAL_R_HairC1': (6, 0.5), 'FACIAL_R_HairC2': (6, 0.5), 'FACIAL_R_HairC3': (6, 0.5),
                    'FACIAL_R_HairC4': (6, 0.5), 'FACIAL_R_JawBulge': (17, 0.5), 'FACIAL_R_JawRecess': (17, 0.5),
                    'FACIAL_R_Jawline': (12, 0.5), 'FACIAL_R_Jawline1': (13, 0.3), 'FACIAL_R_Jawline2': (13, 0.3),
                    'FACIAL_R_LipCorner': (12, 0.7), 'FACIAL_R_LipCorner1': (13, 0.2), 'FACIAL_R_LipCorner2': (13, 0.2),
                    'FACIAL_R_LipCorner3': (13, 0.2), 'FACIAL_R_LipLower': (12, 0.7), 'FACIAL_R_LipLower1': (17, 0.2),
                    'FACIAL_R_LipLower2': (17, 0.2), 'FACIAL_R_LipLower3': (17, 0.2),
                    'FACIAL_R_LipLowerOuter': (12, 0.7),
                    'FACIAL_R_LipLowerOuter1': (17, 0.2), 'FACIAL_R_LipLowerOuter2': (17, 0.2),
                    'FACIAL_R_LipLowerOuter3': (17, 0.2),
                    'FACIAL_R_LipLowerOuterSkin': (14, 0.3), 'FACIAL_R_LipLowerSkin': (14, 0.3),
                    'FACIAL_R_LipUpper': (12, 0.7),
                    'FACIAL_R_LipUpper1': (17, 0.2), 'FACIAL_R_LipUpper2': (17, 0.2), 'FACIAL_R_LipUpper3': (17, 0.2),
                    'FACIAL_R_LipUpperOuter': (12, 0.7), 'FACIAL_R_LipUpperOuter1': (17, 0.2),
                    'FACIAL_R_LipUpperOuter2': (17, 0.2),
                    'FACIAL_R_LipUpperOuter3': (17, 0.2), 'FACIAL_R_LipUpperOuterSkin': (14, 0.3),
                    'FACIAL_R_LipUpperSkin': (14, 0.3),
                    'FACIAL_R_Masseter': (12, 1.0), 'FACIAL_R_NasolabialBulge': (12, 0.6),
                    'FACIAL_R_NasolabialBulge1': (14, 0.4),
                    'FACIAL_R_NasolabialBulge2': (14, 0.4), 'FACIAL_R_NasolabialBulge3': (14, 0.4),
                    'FACIAL_R_NasolabialFurrow': (12, 0.5),
                    'FACIAL_R_NeckA1': (13, 0.3), 'FACIAL_R_NeckA2': (13, 0.3), 'FACIAL_R_NeckA3': (13, 0.3),
                    'FACIAL_R_NeckA4': (13, 0.3), 'FACIAL_R_NeckB1': (13, 0.3), 'FACIAL_R_NeckB2': (13, 0.3),
                    'FACIAL_R_NeckB3': (13, 0.3), 'FACIAL_R_NeckB4': (13, 0.3), 'FACIAL_R_NoseBridge': (13, 0.3),
                    'FACIAL_R_NoseUpper': (17, 0.3), 'FACIAL_R_Nostril': (12, 0.8),
                    'FACIAL_R_NostrilThickness1': (17, 0.2),
                    'FACIAL_R_NostrilThickness2': (17, 0.2), 'FACIAL_R_NostrilThickness3': (17, 0.2),
                    'FACIAL_R_Pupil': (6, 0.6),
                    'FACIAL_R_Sideburn1': (6, 0.5), 'FACIAL_R_Sideburn2': (6, 0.5), 'FACIAL_R_Sideburn3': (6, 0.5),
                    'FACIAL_R_Sideburn4': (6, 0.5), 'FACIAL_R_Sideburn5': (6, 0.5), 'FACIAL_R_Sideburn6': (6, 0.5),
                    'FACIAL_R_Temple': (17, 0.5), 'FACIAL_R_TongueSide2': (6, 0.2), 'FACIAL_R_TongueSide3': (6, 0.2),
                    'FACIAL_L_12IPV_NeckB9': (18, 0.2), 'FACIAL_R_12IPV_NeckB9': (18, 0.2),
                    'FACIAL_L_12IPV_NeckB10': (18, 0.2),
                    'FACIAL_R_12IPV_NeckB10': (18, 0.2), 'FACIAL_L_12IPV_NeckB11': (18, 0.2),
                    'FACIAL_R_12IPV_NeckB11': (18, 0.2),
                    'FACIAL_L_12IPV_NeckB12': (18, 0.2), 'FACIAL_R_12IPV_NeckB12': (18, 0.2),
                    'FACIAL_C_NeckBackB': (13, 0.3),
                    'FACIAL_L_NeckBackB': (13, 0.3), 'FACIAL_R_NeckBackB': (13, 0.3),
                    'FACIAL_C_12IPV_NeckBackB1': (18, 0.2),
                    'FACIAL_C_12IPV_NeckBackB2': (18, 0.2), 'FACIAL_L_12IPV_NeckBackB1': (18, 0.2),
                    'FACIAL_R_12IPV_NeckBackB1': (18, 0.2),
                    'FACIAL_L_12IPV_NeckBackB2': (18, 0.2), 'FACIAL_R_12IPV_NeckBackB2': (18, 0.2),
                    'FACIAL_C_NeckBackA': (13, 0.3),
                    'FACIAL_L_NeckBackA': (13, 0.3), 'FACIAL_R_NeckBackA': (13, 0.3),
                    'FACIAL_C_12IPV_NeckBackA1': (18, 0.2),
                    'FACIAL_C_12IPV_NeckBackA2': (18, 0.2), 'FACIAL_L_12IPV_NeckBackA1': (18, 0.2),
                    'FACIAL_R_12IPV_NeckBackA1': (18, 0.2),
                    'FACIAL_L_12IPV_NeckBackA2': (18, 0.2), 'FACIAL_R_12IPV_NeckBackA2': (18, 0.2)}

    for jointName, jointInfo in jointMapping.iteritems():
        jointNode = pycore.PyNode(jointName)
        jointNode.overrideEnabled.set(True)
        jointNode.overrideColor.set(jointInfo[0])
        jointNode.radius.set(jointInfo[1])


# ****************************************************************************************************
def eyesSetup():
    jntEyeL = "FACIAL_L_Eye"
    locEyeL = "LOC_L_eyeDriver"
    locUIEyeL = "LOC_L_eyeUIDriver"
    locAimEyeL = "LOC_L_eyeAimDriver"
    locAimUpL = "LOC_L_eyeAimUp"
    offGrpEyeL = "GRP_L_eyeAim"
    ctrlEyeL = "CTRL_L_eyeAim"
    ctrlUIEyeL = "CTRL_L_eye"

    jntEyeR = "FACIAL_R_Eye"
    locEyeR = "LOC_R_eyeDriver"
    locUIEyeR = "LOC_R_eyeUIDriver"
    locAimEyeR = "LOC_R_eyeAimDriver"
    locAimUpR = "LOC_R_eyeAimUp"
    offGrpEyeR = "GRP_R_eyeAim"
    ctrlEyeR = "CTRL_R_eyeAim"
    ctrlUIEyeR = "CTRL_R_eye"

    ctrlUIEyeC = "CTRL_C_eye"
    jntFacialRoot = "FACIAL_C_FacialRoot"
    attrAimAt = "CTRL_expressions.lookAtSwitch"
    offGrp = "GRP_C_eyesAim"
    ctrl = "CTRL_C_eyesAim"
    locEyeRoot = "LOC_C_eyeDriver"

    eyeSetup(jntEyeL, locEyeL, locUIEyeL, locAimEyeL, ctrlEyeL, ctrlUIEyeL, attrAimAt, ctrlUIEyeC, locEyeRoot,
             locAimUpL)
    eyeSetup(jntEyeR, locEyeR, locUIEyeR, locAimEyeR, ctrlEyeR, ctrlUIEyeR, attrAimAt, ctrlUIEyeC, locEyeRoot,
             locAimUpR)

    # create visibility switch
    pycore.setDrivenKeyframe((offGrp + ".visibility"), itt="linear", ott="linear", currentDriver=attrAimAt,
                             driverValue=0, value=0)
    pycore.setDrivenKeyframe((offGrp + ".visibility"), itt="linear", ott="linear", currentDriver=attrAimAt,
                             driverValue=1, value=1)

    # connect convergence attribute
    currentTZL = pycore.getAttr(offGrpEyeL + ".tz")
    currentTZR = pycore.getAttr(offGrpEyeR + ".tz")
    pycore.setDrivenKeyframe((offGrpEyeL + ".tz"), itt="linear", ott="linear",
                             currentDriver=("CTRL_convergenceSwitch.ty"), driverValue=0, value=currentTZL)
    pycore.setDrivenKeyframe((offGrpEyeL + ".tz"), itt="linear", ott="linear",
                             currentDriver=("CTRL_convergenceSwitch.ty"), driverValue=1, value=0)
    pycore.setDrivenKeyframe((offGrpEyeR + ".tz"), itt="linear", ott="linear",
                             currentDriver=("CTRL_convergenceSwitch.ty"), driverValue=0, value=currentTZR)
    pycore.setDrivenKeyframe((offGrpEyeR + ".tz"), itt="linear", ott="linear",
                             currentDriver=("CTRL_convergenceSwitch.ty"), driverValue=1, value=0)

    # look direction splines
    pycore.curve(degree=1, point=([0, 0, 0], [0, 0, 0]), knot=(0, 1), name="L_lookDirection")
    pycore.setAttr("L_lookDirection.overrideEnabled", 1)
    pycore.setAttr("L_lookDirection.overrideColor", 1)
    pycore.setAttr("L_lookDirection.overrideDisplayType", 2)
    pycore.curve(degree=1, point=([0, 0, 0], [0, 0, 0]), knot=(0, 1), name="R_lookDirection")
    pycore.setAttr("R_lookDirection.overrideEnabled", 1)
    pycore.setAttr("R_lookDirection.overrideColor", 1)
    pycore.setAttr("R_lookDirection.overrideDisplayType", 2)

    pycore.select("L_lookDirection.cv[0]", r=True)
    pycore.cluster(name="L_lookDirStart")
    pycore.setAttr("L_lookDirStartHandle.visibility", 0)
    pycore.select("L_lookDirection.cv[1]", r=True)
    pycore.cluster(name="L_lookDirEnd")
    pycore.setAttr("L_lookDirEndHandle.visibility", 0)
    pycore.select("R_lookDirection.cv[0]", r=True)
    pycore.cluster(name="R_lookDirStart")
    pycore.setAttr("R_lookDirStartHandle.visibility", 0)
    pycore.select("R_lookDirection.cv[1]", r=True)
    pycore.cluster(name="R_lookDirEnd")
    pycore.setAttr("R_lookDirEndHandle.visibility", 0)

    pycore.pointConstraint(jntEyeL, "L_lookDirStartHandle")
    pycore.pointConstraint(ctrlEyeL, "L_lookDirEndHandle")
    pycore.pointConstraint(jntEyeR, "R_lookDirStartHandle")
    pycore.pointConstraint(ctrlEyeR, "R_lookDirEndHandle")

    # create look direction splines visibility switch
    pycore.setDrivenKeyframe("L_lookDirection.visibility", itt="linear", ott="linear", currentDriver=attrAimAt,
                             driverValue=0, value=0)
    pycore.setDrivenKeyframe("L_lookDirection.visibility", itt="linear", ott="linear", currentDriver=attrAimAt,
                             driverValue=1, value=1)
    pycore.setDrivenKeyframe("R_lookDirection.visibility", itt="linear", ott="linear", currentDriver=attrAimAt,
                             driverValue=0, value=0)
    pycore.setDrivenKeyframe("R_lookDirection.visibility", itt="linear", ott="linear", currentDriver=attrAimAt,
                             driverValue=1, value=1)

    pycore.parent("GRP_convergenceGUI", "CTRL_C_eyesAim")


# ****************************************************************************************************
def eyeSetup(jntEye, locEye, locUIEye, locAimEye, ctrlEye, ctrlUIEye, attrAimAt, ctrlUIEyeC, locEyeRoot, locAimUp):
    jntPos = pycore.xform(jntEye, query=True, worldSpace=True, translation=True)

    # position and create locators
    pycore.xform(locEye, worldSpace=True, absolute=True, translation=jntPos)

    pycore.spaceLocator(name=locUIEye)
    pycore.xform(locUIEye, worldSpace=True, absolute=True, translation=jntPos)
    pycore.setAttr(locUIEye + ".visibility", 0)
    pycore.parent(locUIEye, locEyeRoot)
    pycore.setAttr(locUIEye + ".rx", 0.0)
    pycore.setAttr(locUIEye + ".ry", 0.0)
    pycore.setAttr(locUIEye + ".rz", 0.0)

    pycore.spaceLocator(name=locAimEye)
    pycore.xform(locAimEye, worldSpace=True, absolute=True, translation=jntPos)
    pycore.setAttr(locAimEye + ".visibility", 0)
    pycore.parent(locAimEye, locEyeRoot)
    pycore.setAttr(locAimEye + ".rx", 0.0)
    pycore.setAttr(locAimEye + ".ry", 0.0)
    pycore.setAttr(locAimEye + ".rz", 0.0)

    # connect aim loc
    pycore.aimConstraint(ctrlEye, locAimEye, mo=True, weight=1, aimVector=[0, 0, 1], upVector=[0, 1, 0],
                         worldUpType="object", worldUpObject=locAimUp)
    orientAimCon = pycore.orientConstraint(locAimEye, locEye)

    # connect ui loc to L/R control
    pycore.setDrivenKeyframe((locUIEye + ".ry"), itt="linear", ott="linear", currentDriver=(ctrlUIEye + ".tx"),
                             driverValue=0, value=0)
    pycore.setDrivenKeyframe((locUIEye + ".ry"), itt="linear", ott="linear", currentDriver=(ctrlUIEye + ".tx"),
                             driverValue=1, value=40)
    pycore.setDrivenKeyframe((locUIEye + ".ry"), itt="linear", ott="linear", currentDriver=(ctrlUIEye + ".tx"),
                             driverValue=-1, value=-40)

    pycore.setDrivenKeyframe((locUIEye + ".rx"), itt="linear", ott="linear", currentDriver=(ctrlUIEye + ".ty"),
                             driverValue=0, value=0)
    pycore.setDrivenKeyframe((locUIEye + ".rx"), itt="linear", ott="linear", currentDriver=(ctrlUIEye + ".ty"),
                             driverValue=1, value=-30)
    pycore.setDrivenKeyframe((locUIEye + ".rx"), itt="linear", ott="linear", currentDriver=(ctrlUIEye + ".ty"),
                             driverValue=-1, value=40)

    # connect ui loc to C control
    pycore.setDrivenKeyframe((locUIEye + ".ry"), itt="linear", ott="linear", currentDriver=(ctrlUIEyeC + ".tx"),
                             driverValue=0, value=0)
    pycore.setDrivenKeyframe((locUIEye + ".ry"), itt="linear", ott="linear", currentDriver=(ctrlUIEyeC + ".tx"),
                             driverValue=1, value=40)
    pycore.setDrivenKeyframe((locUIEye + ".ry"), itt="linear", ott="linear", currentDriver=(ctrlUIEyeC + ".tx"),
                             driverValue=-1, value=-40)

    pycore.setDrivenKeyframe((locUIEye + ".rx"), itt="linear", ott="linear", currentDriver=(ctrlUIEyeC + ".ty"),
                             driverValue=0, value=0)
    pycore.setDrivenKeyframe((locUIEye + ".rx"), itt="linear", ott="linear", currentDriver=(ctrlUIEyeC + ".ty"),
                             driverValue=1, value=-30)
    pycore.setDrivenKeyframe((locUIEye + ".rx"), itt="linear", ott="linear", currentDriver=(ctrlUIEyeC + ".ty"),
                             driverValue=-1, value=40)

    orientUICon = pycore.orientConstraint(locUIEye, locEye)

    # create aim at switch
    pycore.setDrivenKeyframe((orientAimCon + "." + locAimEye + "W0"), itt="linear", ott="linear",
                             currentDriver=attrAimAt, driverValue=0, value=0)
    pycore.setDrivenKeyframe((orientAimCon + "." + locAimEye + "W0"), itt="linear", ott="linear",
                             currentDriver=attrAimAt, driverValue=1, value=1)
    pycore.setDrivenKeyframe((orientUICon + "." + locUIEye + "W1"), itt="linear", ott="linear", currentDriver=attrAimAt,
                             driverValue=0, value=1)
    pycore.setDrivenKeyframe((orientUICon + "." + locUIEye + "W1"), itt="linear", ott="linear", currentDriver=attrAimAt,
                             driverValue=1, value=0)


# ************************************************************************************************************
def cleanUp():
    # making groups and hierarchy
    pycore.group(world=True, empty=True, name="head_grp")
    pycore.group(parent="head_grp", empty=True, name="geometry_grp")
    pycore.group(parent="head_grp", empty=True, name="headRig_grp")
    pycore.group(parent="headRig_grp", empty=True, name="headRigging_grp")
    pycore.group(parent="headRig_grp", empty=True, name="headGui_grp")
    pycore.group(parent="headRigging_grp", empty=True, name="eyesSetup_grp")

    pycore.group(parent="head_grp", empty=True, name="morphs_grp")
    pycore.setAttr("morphs_grp.visibility", 0)
    if (pycore.ls("corrective_*")):
        pycore.parent("corrective_*", "morphs_grp")
    pycore.delete("morphs_grp")

    pycore.parent("GRP_C_eyesAim", "headGui_grp")  # eyes aim GUI
    pycore.parent("GRP_faceGUI", "headGui_grp")  # GUI
    if (pycore.ls("*lookDir*")):
        pycore.parent("*lookDir*", "eyesSetup_grp")  # look direction clusters and splines
    pycore.parent("LOC_C_eyeDriver", "eyesSetup_grp")  # eyes setup
    pycore.parentConstraint(["FACIAL_C_FacialRoot", "LOC_C_eyeDriver"], maintainOffset=True)
    # pycore.parent("spine_04", "head_grp")

    # CTRL_expressions visibility
    pycore.setAttr("CTRL_expressions.visibility", keyable=True, lock=False)
    pycore.setAttr("CTRL_expressions.visibility", 0)
    pycore.setAttr("CTRL_expressions.visibility", lock=True, keyable=False, channelBox=False)

    # containers
    pycore.container(name="PSD")
    containers = pycore.ls("*_CONTAINER")
    for container in containers:
        pycore.container("PSD", e=True, addNode=container)

    # deleting body joints animation
    bodyJoints = ["spine_04", "spine_05", "clavicle_l", "upperarm_l", "upperarm_correctiveRoot_l", "upperarm_out_l",
                  "upperarm_fwd_l", "upperarm_in_l", "upperarm_bck_l", "clavicle_out_l", "clavicle_scap_l",
                  "clavicle_r", "upperarm_r", "upperarm_correctiveRoot_r", "upperarm_out_r", "upperarm_fwd_r",
                  "upperarm_in_r", "upperarm_bck_r", "clavicle_out_r", "clavicle_scap_r", "clavicle_pec_l",
                  "clavicle_pec_r", "spine_04_latissimus_l", "spine_04_latissimus_r", "neck_01", "neck_02", "head"]
    for joint in bodyJoints:
        try:
            pycore.delete(joint + "_scaleX", joint + "_scaleY", joint + "_scaleZ", joint + "_translateX",
                          joint + "_translateY", joint + "_translateZ", joint + "_rotateX", joint + "_rotateY",
                          joint + "_rotateZ")
        except:
            pass
    '''
    # add character set
    ctrls = pycore.ls("CTRL_*", type="transform")
    for c in ["CTRL_rigLogic", "CTRL_faceGUI", "CTRL_faceTweakersGUI", "CTRL_L_mouth_lipsPressD", "CTRL_R_mouth_lipsPressD"]:
        ctrls.remove(pycore.PyNode(c))
    pycore.select(ctrls)
    pycore.character(name="Head_CS")
    '''
    # far and near clip plane
    pycore.setAttr("perspShape.nearClipPlane", 5)
    pycore.setAttr("perspShape.farClipPlane", 5000)


def createLODLayerGroups():
    pycore.group(parent="geometry_grp", empty=True, name="head_lod0_grp")
    pycore.group(parent="geometry_grp", empty=True, name="head_lod1_grp")
    pycore.group(parent="geometry_grp", empty=True, name="head_lod2_grp")
    pycore.group(parent="geometry_grp", empty=True, name="head_lod3_grp")
    pycore.group(parent="geometry_grp", empty=True, name="head_lod4_grp")
    pycore.group(parent="geometry_grp", empty=True, name="head_lod5_grp")
    pycore.group(parent="geometry_grp", empty=True, name="head_lod6_grp")
    pycore.group(parent="geometry_grp", empty=True, name="head_lod7_grp")

    pycore.select(clear=True)
    pycore.select("head_lod7_grp", replace=True)
    pycore.createDisplayLayer(name="head_lod7_layer", noRecurse=True)
    pycore.setAttr("head_lod7_layer.visibility", 0)
    pycore.select("head_lod6_grp", replace=True)
    pycore.createDisplayLayer(name="head_lod6_layer", noRecurse=True)
    pycore.setAttr("head_lod6_layer.visibility", 0)
    pycore.select("head_lod5_grp", replace=True)
    pycore.createDisplayLayer(name="head_lod5_layer", noRecurse=True)
    pycore.setAttr("head_lod5_layer.visibility", 0)
    pycore.select("head_lod4_grp", replace=True)
    pycore.createDisplayLayer(name="head_lod4_layer", noRecurse=True)
    pycore.setAttr("head_lod4_layer.visibility", 0)
    pycore.select("head_lod3_grp", replace=True)
    pycore.createDisplayLayer(name="head_lod3_layer", noRecurse=True)
    pycore.setAttr("head_lod3_layer.visibility", 0)
    pycore.select("head_lod2_grp", replace=True)
    pycore.createDisplayLayer(name="head_lod2_layer", noRecurse=True)
    pycore.setAttr("head_lod2_layer.visibility", 0)
    pycore.select("head_lod1_grp", replace=True)
    pycore.createDisplayLayer(name="head_lod1_layer", noRecurse=True)
    pycore.setAttr("head_lod1_layer.visibility", 0)
    pycore.select("head_lod0_grp", replace=True)
    pycore.createDisplayLayer(name="head_lod0_layer", noRecurse=True)
    pycore.setAttr("head_lod0_layer.visibility", 1)
    pycore.select(clear=True)

    # LOD 0
    pycore.parent("head_lod0_mesh", "head_lod0_grp")
    pycore.parent("teeth_lod0_mesh", "head_lod0_grp")
    pycore.parent("saliva_lod0_mesh", "head_lod0_grp")
    pycore.parent("eyeLeft_lod0_mesh", "head_lod0_grp")
    pycore.parent("eyeRight_lod0_mesh", "head_lod0_grp")
    pycore.parent("eyeshell_lod0_mesh", "head_lod0_grp")
    pycore.parent("eyelashes_lod0_mesh", "head_lod0_grp")
    pycore.parent("eyeEdge_lod0_mesh", "head_lod0_grp")
    pycore.parent("cartilage_lod0_mesh", "head_lod0_grp")
    # LOD 1
    pycore.parent("head_lod1_mesh", "head_lod1_grp")
    pycore.parent("teeth_lod1_mesh", "head_lod1_grp")
    pycore.parent("saliva_lod1_mesh", "head_lod1_grp")
    pycore.parent("eyeLeft_lod1_mesh", "head_lod1_grp")
    pycore.parent("eyeRight_lod1_mesh", "head_lod1_grp")
    pycore.parent("eyeshell_lod1_mesh", "head_lod1_grp")
    pycore.parent("eyelashes_lod1_mesh", "head_lod1_grp")
    pycore.parent("eyeEdge_lod1_mesh", "head_lod1_grp")
    pycore.parent("cartilage_lod1_mesh", "head_lod1_grp")
    # LOD 2
    pycore.parent("head_lod2_mesh", "head_lod2_grp")
    pycore.parent("teeth_lod2_mesh", "head_lod2_grp")
    pycore.parent("saliva_lod2_mesh", "head_lod2_grp")
    pycore.parent("eyeLeft_lod2_mesh", "head_lod2_grp")
    pycore.parent("eyeRight_lod2_mesh", "head_lod2_grp")
    pycore.parent("eyeshell_lod2_mesh", "head_lod2_grp")
    pycore.parent("eyelashes_lod2_mesh", "head_lod2_grp")
    pycore.parent("eyeEdge_lod2_mesh", "head_lod2_grp")
    # LOD 3
    pycore.parent("head_lod3_mesh", "head_lod3_grp")
    pycore.parent("teeth_lod3_mesh", "head_lod3_grp")
    pycore.parent("eyeLeft_lod3_mesh", "head_lod3_grp")
    pycore.parent("eyeRight_lod3_mesh", "head_lod3_grp")
    pycore.parent("eyeshell_lod3_mesh", "head_lod3_grp")
    pycore.parent("eyelashes_lod3_mesh", "head_lod3_grp")
    pycore.parent("eyeEdge_lod3_mesh", "head_lod3_grp")
    # LOD 4
    pycore.parent("head_lod4_mesh", "head_lod4_grp")
    pycore.parent("teeth_lod4_mesh", "head_lod4_grp")
    pycore.parent("eyeLeft_lod4_mesh", "head_lod4_grp")
    pycore.parent("eyeRight_lod4_mesh", "head_lod4_grp")
    pycore.parent("eyeshell_lod4_mesh", "head_lod4_grp")
    # LOD 5
    pycore.parent("head_lod5_mesh", "head_lod5_grp")
    pycore.parent("teeth_lod5_mesh", "head_lod5_grp")
    pycore.parent("eyeLeft_lod5_mesh", "head_lod5_grp")
    pycore.parent("eyeRight_lod5_mesh", "head_lod5_grp")
    # LOD 6
    pycore.parent("head_lod6_mesh", "head_lod6_grp")
    pycore.parent("teeth_lod6_mesh", "head_lod6_grp")
    pycore.parent("eyeLeft_lod6_mesh", "head_lod6_grp")
    pycore.parent("eyeRight_lod6_mesh", "head_lod6_grp")
    # LOD 7
    pycore.parent("head_lod7_mesh", "head_lod7_grp")
    pycore.parent("teeth_lod7_mesh", "head_lod7_grp")
    pycore.parent("eyeLeft_lod7_mesh", "head_lod7_grp")
    pycore.parent("eyeRight_lod7_mesh", "head_lod7_grp")


def createLODGroups(dnaProvider):
    MayaUtil.logger.info("Creating LOD hierarchy")
    # LODs hierarchy
    headLODs = []
    distances = [50, 100, 200, 500, 1000, 1500, 2000, 3000]
    for i in xrange(dnaProvider.getLODCount()):
        lodName = "Head_lod%s" % i
        headLODs.append(lodName)
        pycore.group(world=True, empty=True, name=lodName)

    pycore.select(headLODs, replace=True)
    pycore.mel.eval("LevelOfDetailGroup;")
    pycore.rename("LOD_Group_1", "Head_Lx")
    pycore.setAttr("Head_Lx.useScreenHeightPercentage", 0)  # Switch to distance
    pycore.parent("Head_Lx", "geometry_grp")

    for i, val in enumerate(headLODs):
        # set LOD threshold based on distances
        pycore.setAttr("Head_Lx.threshold[%s]" % i, distances[i])
        # rename LOD
        pycore.delete("Head_lod%s" % i)
        pycore.rename("LOD_%s" % i, "Head_lod%s" % i)


def moveHeadMeshesToLODGroups(dnaProvider):
    '''
    Read all mesh names from DNA file and associate them with their corresponding LOD group
    '''
    try:
        for lodLvl in xrange(dnaProvider.getLODCount()):
            for meshIndex in dnaProvider.getMeshIndicesForLOD(lodLvl):
                pycore.parent(dnaProvider.getMeshNameFromIndex(meshIndex), "Head_lod%s" % lodLvl)
    except:
        print("Error moving head meshes to their corresponding LOD groups")
        pass


def getAllHeadMeshNames(dnaProvider):
    retval = []
    try:
        for lodLvl in xrange(dnaProvider.getLODCount()):
            for meshIndex in dnaProvider.getMeshIndicesForLOD(lodLvl):
                meshName = dnaProvider.getMeshNameFromIndex(meshIndex)
                if meshName not in retval:
                    retval.append(meshName)

        return retval
    except:
        print("Error moving head meshes to their corresponding LOD groups")
        pass


def deleteBodyJointsAnimations():
    bodyJoints = ["spine_04", "spine_05", "clavicle_l", "upperarm_l", "upperarm_correctiveRoot_l", "upperarm_out_l",
                  "upperarm_fwd_l", "upperarm_in_l", "upperarm_bck_l", "clavicle_out_l", "clavicle_scap_l",
                  "clavicle_r", "upperarm_r", "upperarm_correctiveRoot_r", "upperarm_out_r", "upperarm_fwd_r",
                  "upperarm_in_r", "upperarm_bck_r", "clavicle_out_r", "clavicle_scap_r", "clavicle_pec_l",
                  "clavicle_pec_r", "spine_04_latissimus_l", "spine_04_latissimus_r", "neck_01", "neck_02", "head"]
    for joint in bodyJoints:
        try:
            pycore.delete(joint + "_scaleX", joint + "_scaleY", joint + "_scaleZ", joint + "_translateX",
                          joint + "_translateY", joint + "_translateZ", joint + "_rotateX", joint + "_rotateY",
                          joint + "_rotateZ")
        except:
            pass


def deliveryCleanUp(dnaProvider):
    # making groups and hierarchy
    pycore.group(world=True, empty=True, name="head_grp")
    pycore.group(parent="head_grp", empty=True, name="geometry_grp")
    pycore.group(parent="head_grp", empty=True, name="headRig_grp")
    pycore.group(parent="headRig_grp", empty=True, name="headRigging_grp")
    pycore.group(parent="headRig_grp", empty=True, name="headGui_grp")
    pycore.group(parent="headRigging_grp", empty=True, name="eyesSetup_grp")

    pycore.group(parent="head_grp", empty=True, name="morphs_grp")
    pycore.setAttr("morphs_grp.visibility", 0)
    if (pycore.ls("corrective_*")):
        pycore.parent("corrective_*", "morphs_grp")
    pycore.delete("morphs_grp")

    pycore.parent("GRP_C_eyesAim", "headGui_grp")  # eyes aim GUI
    pycore.parent("GRP_faceGUI", "headGui_grp")  # GUI
    if (pycore.ls("*lookDir*")):
        pycore.parent("*lookDir*", "eyesSetup_grp")  # look direction clusters and splines
    pycore.parent("LOC_C_eyeDriver", "eyesSetup_grp")  # eyes setup
    pycore.parentConstraint(["FACIAL_C_FacialRoot", "LOC_C_eyeDriver"], maintainOffset=True)
    # pycore.parent("spine_04", "head_grp")
    # pycore.setAttr("BODY_C_Spine4.visibility", 0)
    connectNeckCorrectives()
    # createLODGroups(dnaProvider)
    # moveHeadMeshesToLODGroups(dnaProvider)
    createLODLayerGroups()

    # CTRL_expressions visibility
    pycore.setAttr("CTRL_expressions.visibility", keyable=True, lock=False)
    pycore.setAttr("CTRL_expressions.visibility", 0)
    pycore.setAttr("CTRL_expressions.visibility", lock=True, keyable=False, channelBox=False)

    # containers
    pycore.container(name="PSD")
    containers = pycore.ls("*_CONTAINER")
    for container in containers:
        pycore.container("PSD", e=True, addNode=container)

    deleteBodyJointsAnimations()
    '''
    # add character set
    ctrls = pycore.ls("CTRL_*", type="transform")
    for c in ["CTRL_rigLogic", "CTRL_faceGUI", "CTRL_faceTweakersGUI", "CTRL_L_mouth_lipsPressD", "CTRL_R_mouth_lipsPressD"]:
        ctrls.remove(pycore.PyNode(c))
    pycore.select(ctrls)
    pycore.character(name="Head_CS")
    '''
    # far and near clip plane
    pycore.setAttr("perspShape.nearClipPlane", 5)
    pycore.setAttr("perspShape.farClipPlane", 5000)


def orientScene(orientation, meshNames):
    import DHI.core.consts as consts

    MayaUtil.adaptScene(consts.SCALE, consts.SCALE_PIVOT, orientation, consts.TRANSLATE_FACTOR, meshNames,
                        consts.GUI_NAMES,
                        consts.CONTROL_NAMES)

    MayaUtil.logger.info("----Embedded scene adapted.")


def connectNeckCorrectives():
    if pycore.objExists("neck_01.rx") and pycore.objExists("LOC_neck01JointInput.rx"):
        pycore.connectAttr("neck_01.rx", "LOC_neck01JointInput.rx")

    if pycore.objExists("neck_01.ry") and pycore.objExists("LOC_neck01JointInput.ry"):
        pycore.connectAttr("neck_01.ry", "LOC_neck01JointInput.ry")

    if pycore.objExists("neck_01.rz") and pycore.objExists("LOC_neck01JointInput.rz"):
        pycore.connectAttr("neck_01.rz", "LOC_neck01JointInput.rz")

    if pycore.objExists("neck_02.rx") and pycore.objExists("LOC_neck02JointInput.rx"):
        pycore.connectAttr("neck_02.rx", "LOC_neck02JointInput.rx")

    if pycore.objExists("neck_02.ry") and pycore.objExists("LOC_neck02JointInput.ry"):
        pycore.connectAttr("neck_02.ry", "LOC_neck02JointInput.ry")

    if pycore.objExists("neck_02.rz") and pycore.objExists("LOC_neck02JointInput.rz"):
        pycore.connectAttr("neck_02.rz", "LOC_neck02JointInput.rz")

    if pycore.objExists("head.rx") and pycore.objExists("LOC_headJointInput.rx"):
        pycore.connectAttr("head.rx", "LOC_headJointInput.rx")

    if pycore.objExists("head.ry") and pycore.objExists("LOC_headJointInput.ry"):
        pycore.connectAttr("head.ry", "LOC_headJointInput.ry")

    if pycore.objExists("head.rz") and pycore.objExists("LOC_headJointInput.rz"):
        pycore.connectAttr("head.rz", "LOC_headJointInput.rz")

    if pycore.objExists("LOC_expListOutputToRL.headTurnUpU") and pycore.objExists("CTRL_expressions.headTurnUpU"):
        pycore.connectAttr("LOC_expListOutputToRL.headTurnUpU", "CTRL_expressions.headTurnUpU")

    if pycore.objExists("LOC_expListOutputToRL.headTurnUpM") and pycore.objExists("CTRL_expressions.headTurnUpM"):
        pycore.connectAttr("LOC_expListOutputToRL.headTurnUpM", "CTRL_expressions.headTurnUpM")

    if pycore.objExists("LOC_expListOutputToRL.headTurnUpD") and pycore.objExists("CTRL_expressions.headTurnUpD"):
        pycore.connectAttr("LOC_expListOutputToRL.headTurnUpD", "CTRL_expressions.headTurnUpD")

    if pycore.objExists("LOC_expListOutputToRL.headTurnDownU") and pycore.objExists("CTRL_expressions.headTurnDownU"):
        pycore.connectAttr("LOC_expListOutputToRL.headTurnDownU", "CTRL_expressions.headTurnDownU")

    if pycore.objExists("LOC_expListOutputToRL.headTurnDownM") and pycore.objExists("CTRL_expressions.headTurnDownM"):
        pycore.connectAttr("LOC_expListOutputToRL.headTurnDownM", "CTRL_expressions.headTurnDownM")

    if pycore.objExists("LOC_expListOutputToRL.headTurnDownD") and pycore.objExists("CTRL_expressions.headTurnDownD"):
        pycore.connectAttr("LOC_expListOutputToRL.headTurnDownD", "CTRL_expressions.headTurnDownD")

    if pycore.objExists("LOC_expListOutputToRL.headTurnLeftU") and pycore.objExists("CTRL_expressions.headTurnLeftU"):
        pycore.connectAttr("LOC_expListOutputToRL.headTurnLeftU", "CTRL_expressions.headTurnLeftU")

    if pycore.objExists("LOC_expListOutputToRL.headTurnLeftM") and pycore.objExists("CTRL_expressions.headTurnLeftM"):
        pycore.connectAttr("LOC_expListOutputToRL.headTurnLeftM", "CTRL_expressions.headTurnLeftM")

    if pycore.objExists("LOC_expListOutputToRL.headTurnLeftD") and pycore.objExists("CTRL_expressions.headTurnLeftD"):
        pycore.connectAttr("LOC_expListOutputToRL.headTurnLeftD", "CTRL_expressions.headTurnLeftD")

    if pycore.objExists("LOC_expListOutputToRL.headTurnRightU") and pycore.objExists("CTRL_expressions.headTurnRightU"):
        pycore.connectAttr("LOC_expListOutputToRL.headTurnRightU", "CTRL_expressions.headTurnRightU")

    if pycore.objExists("LOC_expListOutputToRL.headTurnRightM") and pycore.objExists("CTRL_expressions.headTurnRightM"):
        pycore.connectAttr("LOC_expListOutputToRL.headTurnRightM", "CTRL_expressions.headTurnRightM")

    if pycore.objExists("LOC_expListOutputToRL.headTurnRightD") and pycore.objExists("CTRL_expressions.headTurnRightD"):
        pycore.connectAttr("LOC_expListOutputToRL.headTurnRightD", "CTRL_expressions.headTurnRightD")

    if pycore.objExists("LOC_expListOutputToRL.headTiltLeftU") and pycore.objExists("CTRL_expressions.headTiltLeftU"):
        pycore.connectAttr("LOC_expListOutputToRL.headTiltLeftU", "CTRL_expressions.headTiltLeftU")

    if pycore.objExists("LOC_expListOutputToRL.headTiltLeftM") and pycore.objExists("CTRL_expressions.headTiltLeftM"):
        pycore.connectAttr("LOC_expListOutputToRL.headTiltLeftM", "CTRL_expressions.headTiltLeftM")

    if pycore.objExists("LOC_expListOutputToRL.headTiltLeftD") and pycore.objExists("CTRL_expressions.headTiltLeftD"):
        pycore.connectAttr("LOC_expListOutputToRL.headTiltLeftD", "CTRL_expressions.headTiltLeftD")

    if pycore.objExists("LOC_expListOutputToRL.headTiltRightU") and pycore.objExists("CTRL_expressions.headTiltRightU"):
        pycore.connectAttr("LOC_expListOutputToRL.headTiltRightU", "CTRL_expressions.headTiltRightU")

    if pycore.objExists("LOC_expListOutputToRL.headTiltRightM") and pycore.objExists("CTRL_expressions.headTiltRightM"):
        pycore.connectAttr("LOC_expListOutputToRL.headTiltRightM", "CTRL_expressions.headTiltRightM")

    if pycore.objExists("LOC_expListOutputToRL.headTiltRightD") and pycore.objExists("CTRL_expressions.headTiltRightD"):
        pycore.connectAttr("LOC_expListOutputToRL.headTiltRightD", "CTRL_expressions.headTiltRightD")


def adjustACGuiPosition(gender, height):
    ######################################################################
    # get facialRoot and eye joints positions
    facialRootPosition = pycore.xform("FACIAL_C_FacialRoot", worldSpace=True, translation=True, query=True)
    leftEyePosition = pycore.xform("FACIAL_L_Eye", worldSpace=True, translation=True, query=True)
    rightEyePosition = pycore.xform("FACIAL_R_Eye", worldSpace=True, translation=True, query=True)
    # arithmetic mean between eye joints
    middleEyesXPosition = ((leftEyePosition[0] + rightEyePosition[0]) / 2)
    middleEyesYPosition = ((leftEyePosition[1] + rightEyePosition[1]) / 2)
    middleEyesZPosition = ((leftEyePosition[2] + rightEyePosition[2]) / 2)
    middleEyesPosition = (middleEyesXPosition, middleEyesYPosition, middleEyesZPosition)
    # postitioning objects on correct positions
    pycore.move(facialRootPosition[0], facialRootPosition[1], facialRootPosition[2], "LOC_C_eyeDriver",
                absolute=True)
    pycore.parent("LOC_L_eyeAimUp", "LOC_L_eyeDriver")
    pycore.move(leftEyePosition[0], leftEyePosition[1], leftEyePosition[2], "LOC_L_eyeDriver", absolute=True)
    pycore.parent("LOC_L_eyeAimUp", "LOC_C_eyeDriver")
    pycore.parent("LOC_R_eyeAimUp", "LOC_R_eyeDriver")
    pycore.move(rightEyePosition[0], rightEyePosition[1], rightEyePosition[2], "LOC_R_eyeDriver", absolute=True)
    pycore.parent("LOC_R_eyeAimUp", "LOC_C_eyeDriver")

    acDistanceFromHead = 20.465
    resolvedScale = getGUIScale(gender, height)
    if resolvedScale:
        acDistanceFromHead = acDistanceFromHead * resolvedScale

    pycore.move(middleEyesPosition[0], middleEyesPosition[1] - acDistanceFromHead, middleEyesPosition[2],
                "GRP_C_eyesAim",
                absolute=True)
    pycore.parent("GRP_L_eyeAim", world=True)
    pycore.move(leftEyePosition[0], leftEyePosition[1], leftEyePosition[2], "GRP_L_eyeAim", absolute=True)
    pycore.parent("GRP_L_eyeAim", "CTRL_C_eyesAim")
    pycore.setAttr("GRP_L_eyeAim.translateY", 0.0)
    pycore.parent("GRP_R_eyeAim", world=True)
    pycore.move(rightEyePosition[0], rightEyePosition[1], rightEyePosition[2], "GRP_R_eyeAim", absolute=True)
    pycore.parent("GRP_R_eyeAim", "CTRL_C_eyesAim")
    pycore.setAttr("GRP_R_eyeAim.translateY", 0.0)
    pycore.select(clear=True)

# ****************************************************************************************************
def getGUIScale(gender, height):
    from DHI.core.consts import GUI_SCALES
    val = "_".join([gender, height])
    if val in GUI_SCALES:
        return GUI_SCALES[val]
    else:
        return None


def interfacePostAssemble(dnaProvider, sceneOrientation, gender, height):
    MayaUtil.logger.info("Post assemble scripts reached. Calling orientation")
    orientScene(sceneOrientation, getAllHeadMeshNames(dnaProvider))
    MayaUtil.logger.info("Connecting all expressions")
    connectAllExpressions()
    MayaUtil.logger.info("Adjusting AC GUI position")
    adjustACGuiPosition(gender, height)
    MayaUtil.logger.info("Eye setup")
    eyesSetup()
    MayaUtil.logger.info("Defauly Lambert shader")
    defaultLambertShader()
    MayaUtil.logger.info("Delivery cleanup")
    deliveryCleanUp(dnaProvider)
