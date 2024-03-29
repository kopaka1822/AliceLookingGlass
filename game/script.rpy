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
define wqueen = Character("White Queen", color="#ffffff")
define wking = Character("White King", color="#ffffff")
define rqueen = Character("Red Queen", color="#ff0000")
define rking = Character("Red King", color="#ff0000")

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

    "One thing was certain, that the white kitten had had nothing to do with it:—it was the black kitten’s fault entirely."
    "For the white kitten had been having its face washed by the old cat for the last quarter of an hour (and bearing it pretty well, considering); so you see that it couldn’t have had any hand in the mischief."

    "The way Dinah washed her children’s faces was this: first she held the poor thing down by its ear with one paw, and then with the other paw she rubbed its face all over, the wrong way, beginning at the nose."
    
    "And just now, as I said, she was hard at work on the white kitten, which was lying quite still and trying to purr—no doubt feeling that it was all meant for its good."

    "But the black kitten had been finished with earlier in the afternoon, and so, while Alice was sitting curled up in a corner of the great arm-chair, half talking to herself and half asleep, the kitten had been having a grand game of romps with the ball of worsted Alice had been trying to wind up, and had been rolling it up and down till it had all come undone again;"
    
    "And there it was, spread over the hearth-rug, all knots and tangles, with the kitten running after its own tail in the middle."

    alice "Oh, you wicked little thing!"
    "She was catching up to the kitten, and giving it a little kiss to make it understand that it was in disgrace."
    
    alice "Really, Dinah ought to have taught you better manners! You ought, Dinah, you know you ought!" # She was looking reproachfully at the old cat, and speaking in as cross a voice as she could manage

    "She scrambled back into the arm-chair, taking the kitten and the worsted with her, and began winding up the ball again."

    "But she didn’t get on very fast, as she was talking all the time, sometimes to the kitten, and sometimes to herself."

    "Kitty sat very demurely on her knee, pretending to watch the progress of the winding, and now and then putting out one paw and gently touching the ball, as if it would be glad to help, if it might."

    alice "Do you know what to-morrow is, Kitty?"
    alice "You’d have guessed if you’d been up in the window with me—only Dinah was making you tidy, so you couldn’t."
    alice "I was watching the boys getting in sticks for the bonfire—and it wants plenty of sticks, Kitty!"
    alice "Only it got so cold, and it snowed so, they had to leave off."
    alice "Never mind, Kitty, we’ll go and see the bonfire to-morrow."
    "Here Alice wound two or three turns of the worsted round the kitten’s neck, just to see how it would look: this led to a scramble, in which the ball rolled down upon the floor, and yards and yards of it got unwound again."

    alice "Do you know, I was so angry, Kitty, when I saw all the mischief you had been doing, I was very nearly opening the window, and putting you out into the snow!"
    alice "And you’d have deserved it, you little mischievous darling!"
    alice "What have you got to say for yourself? Now don’t interrupt me!" 
    "She went on, holding up one finger."
    alice "I’m going to tell you all your faults."
    alice "Number one: you squeaked twice while Dinah was washing your face this morning."
    alice "Now you can’t deny it, Kitty: I heard you!"
    alice "What’s that you say?"
    "(She was pretending that the kitten was speaking)"
    alice "Her paw went into your eye?"
    alice "Well, that’s your fault, for keeping your eyes open—if you’d shut them tight up, it wouldn’t have happened."
    alice "Now don’t make any more excuses, but listen!"
    alice "Number two: you pulled Snowdrop away by the tail just as I had put down the saucer of milk before her!"
    alice "What, you were thirsty, were you?"
    alice "How do you know she wasn’t thirsty too?"
    alice "Now for number three: you unwound every bit of the worsted while I wasn’t looking!"

    alice "That’s three faults, Kitty, and you’ve not been punished for any of them yet."
    alice "You know I’m saving up all your punishments for Wednesday week—Suppose they had saved up all my punishments!"
    # She went on, talking more to herself than the kitten.
    alice "What would they do at the end of a year?"
    alice "I should be sent to prison, I suppose, when the day came."
    alice "Or—let me see—suppose each punishment was to be going without a dinner: then, when the miserable day came, I should have to go without fifty dinners at once!"
    alice "Well, I shouldn’t mind that much! I’d far rather go without them than eat them!"

    alice "Do you hear the snow against the window-panes, Kitty? How nice and soft it sounds!"
    alice "Just as if some one was kissing the window all over outside."
    alice "I wonder if the snow loves the trees and fields, that it kisses them so gently?"
    alice "And then it covers them up snug, you know, with a white quilt; and perhaps it says, ‘Go to sleep, darlings, till the summer comes again.’"
    alice "And when they wake up in the summer, Kitty, they dress themselves all in green, and dance about—whenever the wind blows—oh, that’s very pretty!"
    # cried Alice, dropping the ball of worsted to clap her hands.
    "Alice dropped the ball of worsted to clap her hands."
    alice "And I do so wish it was true!"
    alice "I’m sure the woods look sleepy in the autumn, when the leaves are getting brown."

    alice "Kitty, can you play chess?"
    alice "Now, don’t smile, my dear, I’m asking it seriously."
    alice "Because when we were playing just now, you watched just as if you understood it: and when I said ‘Check!’ you purred!"
    alice "Well, it was a nice check, Kitty, and really I might have won, if it hadn’t been for that nasty Knight, that came wiggling down among my pieces."
    #alice "Kitty, dear, let’s pretend—"

    # narrator stuff to be skipped
    # And here I wish I could tell you half the things Alice used to say, beginning with her favourite phrase “Let’s pretend.” She had had quite a long argument with her sister only the day before—all because Alice had begun with “Let’s pretend we’re kings and queens;” and her sister, who liked being very exact, had argued that they couldn’t, because there were only two of them, and Alice had been reduced at last to say, “Well, _you_ can be one of them then, and _I’ll_ be all the rest.” And once she had really frightened her old nurse by shouting suddenly in her ear, “Nurse! Do let’s pretend that I’m a hungry hyaena, and you’re a bone. But this is taking us away from Alice’s speech to the kitten.

    alice "Let’s pretend that you’re the Red Queen, Kitty!"
    alice "Do you know, I think if you sat up and folded your arms, you’d look exactly like her."
    alice "Now do try, there’s a dear!"
    "And Alice got the Red Queen off the table, and set it up before the kitten as a model for it to imitate: however, the thing didn’t succeed, principally, Alice said, because the kitten wouldn’t fold its arms properly."
    "So, to punish it, she held it up to the Looking-glass, that it might see how sulky it was"
    alice "And if you’re not good directly, I’ll put you through into Looking-glass House. How would you like that?’"

    alice "Now, if you’ll only attend, Kitty, and not talk so much, I’ll tell you all my ideas about Looking-glass House."
    alice "First, there’s the room you can see through the glass—that’s just the same as our drawing room, only the things go the other way."
    alice "I can see all of it when I get upon a chair—all but the bit behind the fireplace."
    alice "Oh! I do so wish I could see that bit!"
    alice "I want so much to know whether they’ve a fire in the winter: you never can tell, you know, unless our fire smokes, and then smoke comes up in that room too—but that may be only pretence, just to make it look as if they had a fire."
    alice "Well then, the books are something like our books, only the words go the wrong way; I know that, because I’ve held up one of our books to the glass, and then they hold up one in the other room."

    alice "How would you like to live in Looking-glass House, Kitty?"
    alice "I wonder if they’d give you milk in there?"
    alice "Perhaps Looking-glass milk isn’t good to drink—But oh, Kitty! Now we come to the passage."
    alice "You can just see a little peep of the passage in Looking-glass House, if you leave the door of our drawing-room wide open: and it’s very like our passage as far as you can see, only you know it may be quite different on beyond."
    alice "Oh, Kitty! how nice it would be if we could only get through into Looking-glass House!"
    alice "I’m sure it’s got, oh! such beautiful things in it! Let’s pretend there’s a way of getting through into it, somehow, Kitty."
    alice "Let’s pretend the glass has got all soft like gauze, so that we can get through."
    alice "Why, it’s turning into a sort of mist now, I declare! It’ll be easy enough to get through—"
    "She was up on the chimney-piece while she said this, though she hardly knew how she had got there."
    "And certainly the glass was beginning to melt away, just like a bright silvery mist."

    "In another moment Alice was through the glass, and had jumped lightly down into the Looking-glass room."
    "The very first thing she did was to look whether there was a fire in the fireplace, and she was quite pleased to find that there was a real one, blazing away as brightly as the one she had left behind."

    alice "(So I shall be as warm here as I was in the old room)"
    alice "(Warmer, in fact, because there’ll be no one here to scold me away from the fire)"
    alice "(Oh, what fun it’ll be, when they see me through the glass in here, and can’t get at me!)"

    "Then she began looking about, and noticed that what could be seen from the old room was quite common and uninteresting, but that all the rest was as different as possible."
    "For instance, the pictures on the wall next the fire seemed to be all alive, and the very clock on the chimney-piece (you know you can only see the back of it in the Looking-glass) had got the face of a little old man, and grinned at her."

    alice "(They don’t keep this room so tidy as the other)" 
    "She noticed several of the chessmen down in the hearth among the cinders: but in another moment, with a little “Oh!” of surprise, she was down on her hands and knees watching them."
    "The chessmen were walking about, two and two!"

    alice "*whispering* Here are the Red King and the Red Queen, and there are the White King and the White Queen sitting on the edge of the shovel."
    alice "And here are two castles walking arm in arm."
    alice "I don’t think they can hear me."
    "She puts her head closer down."
    alice "And I’m nearly sure they can’t see me."
    alice "I feel somehow as if I were invisible—"

    "Here something began squeaking on the table behind Alice, and made her turn her head just in time to see one of the White Pawns roll over and begin kicking: she watched it with great curiosity to see what would happen next."

    wqueen "It is the voice of my child!"
    "The White Queen rushed past the King, so violently that she knocked him over among the cinders."
    wqueen "My precious Lily! My imperial kitten!"
    "And she began scrambling wildly up the side of the fender."

    wking "Imperial fiddlestick!"
    "The king was rubbing his nose, which had been hurt by the fall."
    "He had a right to be a little annoyed with the Queen, for he was covered with ashes from head to foot."

    "Alice was very anxious to be of use, and, as the poor little Lily was nearly screaming herself into a fit, she hastily picked up the Queen and set her on the table by the side of her noisy little daughter."

    "The Queen gasped, and sat down: the rapid journey through the air had quite taken away her breath, and for a minute or two she could do nothing but hug the little Lily in silence."

    "As soon as she had recovered her breath a little, she called out to the White King, who was sitting sulkily among the ashes."
    wqueen "Mind the volcano!"

    wking "What volcano?"
    "The King was looking up anxiously into the fire, as if he thought that was the most likely place to find one."

    wqueen "*panting* Blew—me—up—, Mind you come up—the regular way—don’t get blown up!"

    "Alice watched the White King as he slowly struggled up from bar to bar."

    wqueen "Why, you’ll be hours and hours getting to the table, at that rate."
    wqueen "I’d far better help you, hadn’t I?"
    "But the King took no notice of the question: it was quite clear that he could neither hear her nor see her."

    "So Alice picked him up very gently, and lifted him across more slowly than she had lifted the Queen, that she might not take his breath away: but, before she put him on the table, she thought she might as well dust him a little, he was so covered with ashes."

    "She said afterwards that she had never seen in all her life such a face as the King made, when he found himself held in the air by an invisible hand, and being dusted: he was far too much astonished to cry out, but his eyes and his mouth went on getting larger and larger, and rounder and rounder, till her hand shook so with laughing that she nearly let him drop upon the floor."

    alice "Oh! please don’t make such faces, my dear!"
    alice "You make me laugh so that I can hardly hold you!"
    alice "And don’t keep your mouth so wide open! All the ashes will get into it—there, now I think you’re tidy enough!"
    # "She added as she smoothed his hair, and set him upon the table near the Queen."
    "She set him upon the table near the Queen."

    

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