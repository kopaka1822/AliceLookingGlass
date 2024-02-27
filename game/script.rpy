init python:
    import random
    import time

    # remove mouse wheel from rollback (its annoying in the browser)
    config.keymap['rollback'] = ['any_K_PAGEUP', 'any_KP_PAGEUP', 'K_AC_BACK']
    config.keymap['rollforward'] = ['any_K_PAGEDOWN', 'any_KP_PAGEDOWN']

    renpy.register_shader("game.breathing", variables="""
        uniform sampler2D tex0;
        uniform float u_time;
        uniform float u_breath_cycle;
        uniform float u_offset; // in 0 1
        uniform vec2 res0;
        varying vec2 v_tex_coord;
    """, fragment_300="""
        float scale = 0.5 + 0.5 * sin((u_offset + u_time / u_breath_cycle) * 2.0 * 3.141);
        #ifndef TEXC
        vec2 texC = v_tex_coord.xy;
        #endif
        texC.y = 1.0 - (1.0 - texC.y) * (1.0 + 0.01 * scale);
        if(texC.y < 0.0 || texC.y > 1.0) discard;

        gl_FragColor = texture2D(tex0, texC, -0.55);
    """)
    renpy.register_shader("game.animation", variables="""
        uniform sampler2D tex0;
        uniform sampler2D tex1;
        uniform float u_time;
        uniform float u_breath_cycle;
        uniform float u_offset; // in 0 1
        varying vec2 v_tex_coord;
    """, fragment_250="""
        float a = texture2D(tex1, v_tex_coord, -0.5).x;
        #define TEXC
        vec2 texC = v_tex_coord.xy;
        float xspread = -(texC.x - 0.5) * (1.0 + sin((u_offset + u_time / u_breath_cycle) * 2.0 * 3.141)) * a * 0.04;
        texC.x += xspread;
        texC.y += cos((u_offset + u_time / u_breath_cycle) * 2.0 * 3.141) * a * 0.006;
        gl_FragColor = texture2D(tex0, texC, -0.5);
    """)

    renpy.register_shader("game.wind", variables="""
        uniform sampler2D tex0;
        uniform sampler2D tex1;
        uniform float u_time;
        uniform vec2 res0;
        varying vec2 v_tex_coord;
    """, fragment_300="""
        float a = texture2D(tex1, v_tex_coord, 0.5).x;
        #define TEXC
        vec2 texC = v_tex_coord.xy;
        if(a > 0.0){
            // original from https://github.com/bitsawer/renpy-shader/blob/master/ShaderDemo/game/shader/shadercode.py
            const float FLUIDNESS = 0.75;
            const float WIND_SPEED = 1.0;
            const float DISTANCE = 2.0;
            vec2 pixel = texC * res0; // calc in pixel coordinates to be independent for wider images
            float modifier = sin(pixel.x * 0.006 + u_time) / 2.0 + 1.5;
            texC.x += sin(pixel.x * 0.006 * FLUIDNESS + u_time * WIND_SPEED) * modifier * a * (DISTANCE / res0.x);
            texC.y += cos(pixel.y * 0.02 * FLUIDNESS + u_time * WIND_SPEED) * a * (DISTANCE / res0.y);
        }
        gl_FragColor = texture2D(tex0, texC, -0.5);
    """)
    renpy.register_shader("game.mask2", variables="""
        uniform sampler2D tex0;
        uniform sampler2D tex2;
        varying vec2 v_tex_coord;
    """, fragment_500="""
        #ifndef TEXC
        vec2 texC = v_tex_coord.xy;
        #endif
        float alphaMask = texture2D(tex2, texC, -0.5).a;
        gl_FragColor = texture2D(tex0, texC, -0.5) * alphaMask;
    """)

    def get_shaders_breathing(child):
        if isinstance(child.target, renpy.display.im.Image):
            return ["renpy.texture", "game.breathing"]
        return ["renpy.texture", "game.animation", "game.breathing"]

    def get_shaders_swimming(child):
        if isinstance(child.target, renpy.display.im.Image):
            return ["renpy.texture"]
        return ["renpy.texture", "game.animation"]

    def get_object_rng(obj):
        if isinstance(obj, renpy.display.image.ImageReference):
            return (hash(obj.name[0]) % 7919) / 7919
        return 0.0

define alice = Character("Alice", color="#ADD8E6")
define everyone = Character("Everyone", color="#ffffff")
define anon = Character("???", color="#ffffff")

define alice_scale = 0.5

define cam_transition = 0.5
define center_offset = 540 # half of 1080


## ANIMATED TRANSFORMS ##
## remove comment below to work with action editor
#'''
transform breathing_calm(child):
    child
    anchor (0.5, 1.0)
    #$ shaders = ["renpy.texture", "game.animation", "game.breathing"]
    shader get_shaders_breathing(child)
    u_breath_cycle 6.0
    u_offset get_object_rng(child)
    pause 0
    repeat

transform breathing(child):
    child
    anchor (0.5, 1.0)
    shader get_shaders_breathing(child)
    u_breath_cycle 5.0
    u_offset get_object_rng(child)
    pause 0
    repeat

transform breathing_crying(child):
    child
    anchor (0.5, 1.0)
    shader get_shaders_breathing(child)
    u_offset get_object_rng(child)
    #u_breath_cycle 3.5
    u_breath_cycle 5.0
    pause 0
    repeat

transform swimming(child):
    child
    anchor (0.5, 1.0)
    shader get_shaders_swimming(child)
    u_breath_cycle 5.0
    u_offset get_object_rng(child)
    ease 2.0 yoffset -10 
    ease 2.0 yoffset 10
    # TODO maybe add breathing anim.
    repeat

transform windy(child):
    anchor (0.5,0)
    pos(0.0,0)
    xoffset center_offset
    child
    shader ["renpy.texture", "game.wind"]
    pause 0
    repeat

transform windy_no_anchor(child):
    child
    shader ["renpy.texture", "game.wind"]
    pause 0
    repeat

transform windy_mask(child):
    anchor (0.5,0)
    pos(0.0,0)
    xoffset center_offset
    child
    shader ["renpy.texture", "game.wind", "game.mask2"]
    pause 0
    repeat

# alice pictures
image alice sleepy = Model().child("alice sleepy.png", fit=True).texture("alice_mask.png")
image alice crying = Model().child("alice crying.png", fit=True).texture("alice_mask.png")
image alice excited = Model().child("alice excited.png", fit=True).texture("alice_mask.png")
image alice happy = Model().child("alice happy.png", fit=True).texture("alice_mask.png")
image alice normal = Model().child("alice normal.png", fit=True).texture("alice_mask.png")
image alice pout = Model().child("alice pout.png", fit=True).texture("alice_mask.png")
image alice surprised = Model().child("alice surprised.png", fit=True).texture("alice_mask.png")
image alice thinking = Model().child("alice thinking.png", fit=True).texture("alice_mask.png")

'''

# non-animated transforms (comment in for action editor)
transform breathing_calm:
    anchor (0.5, 1.0)

transform breathing:
    anchor (0.5, 1.0)

transform breathing_crying:
    anchor (0.5, 1.0)

transform swimming:
    anchor (0.5, 1.0)
    ease 2.0 yoffset -10 
    ease 2.0 yoffset 10
    repeat

transform windy:
    anchor (0.5,0)
    pos (0,0)
    xoffset center_offset

transform windy_no_anchor:
    xoffset 0 # do nothing

transform windy_mask:
    anchor (0.5,0)
    pos (0,0)
    xoffset center_offset

#'''
# end comment out



# general transforms / lables
transform anchor:
    anchor (0.5, 1.0)

label reset_camera:
    camera:
        perspective False
        xpos 0 ypos 0 zpos 0 zoom 1.0 xoffset 0 zrotate 0
    return

label start:
    # select language on first start
    call screen language

label chapter1:
    scene black
    call reset_camera
    "{size=+40}Chapter I: \n{/size}Looking-Glass House"


label chapter2:
    scene black
    call reset_camera
    "{size=+40}Chapter II: \n{/size}The Garden of Live Flowers"

label chapter3:
    scene black
    call reset_camera
    "{size=+40}Chapter III: \n{/size}Looking-Glass Insects"

label chapter4:
    scene black
    call reset_camera
    "{size=+40}Chapter IV: \n{/size}Tweedledum and Tweedledee"

label chapter5:
    scene black
    call reset_camera
    "{size=+40}Chapter V: \n{/size}Wool and Water"

label chapter6:
    scene black
    call reset_camera
    "{size=+40}Chapter VI: \n{/size}Humpty Dumpty"

label chapter7:
    scene black
    call reset_camera
    "{size=+40}Chapter VII: \n{/size}The Lion and the Unicorn"

label chapter8:
    scene black
    call reset_camera
    "{size=+40}Chapter VIII: \n{/size}It's My Own Invention"

label chapter9:
    scene black
    call reset_camera
    "{size=+40}Chapter IX: \n{/size}Queen Alice"

label chapter10:
    scene black
    call reset_camera
    "{size=+40}Chapter X: \n{/size}Shaking"

label chapter11:
    scene black
    call reset_camera
    "{size=+40}Chapter XI: \n{/size}Waking"

label chapter12:
    scene black
    call reset_camera
    "{size=+40}Chapter XII: \n{/size}Which Dreamed It?"

    scene black
    call reset_camera
    "The End."
    
    call screen credits
    # delete autosave slot
    if renpy.can_load("auto-1"):
        $ renpy.unlink_save("auto-1")
    return

label autoload:
    if renpy.can_load("auto-1"):
        $ renpy.load("auto-1")
    jump start
    return