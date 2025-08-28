from interactions import *
import random

class Cucumber(Extension):

    snails = [
        'https://cdn.discordapp.com/attachments/158964992756940800/1365625571664724009/moonrabbit4.gif?ex=68b2202c&is=68b0ceac&hm=f5c5b3471e7ba80cc6f4a66f3909dca5ea7e6de18884a8e2c0115591d20d0fa9&',
        'https://tenor.com/view/snail-house-nod-gif-24574765',
        'https://tenor.com/view/snailchan-ko-knock-out-knockout-snail-chan-gif-3981377937711190590',
        'https://tenor.com/view/snail-chan-gif-22638071',
        'https://tenor.com/view/snailchan-sleeping-sleep-dreaming-dream-gif-3131111459738020825',
        'https://tenor.com/view/snail%27s-house-utakata-snail-gif-7748582865504495204',
        'https://tenor.com/view/snails-house-snail%27s-house-guruguru-ujico-snail%27s-house---guruguru-gif-12194613408187795589',
        'https://tenor.com/view/snail-chan-sleep-speedoru-snails-house-gif-14046613515158186533',
        'https://tenor.com/view/snails-house-snail-witch-wandering-ghost-ujico-gif-24230446',
        'https://tenor.com/view/ujico-snail-house-kokoro-travel-gif-4006415686321967804',
        'https://tenor.com/view/moon-rabbit-snail%27s-house-alien-pop-snail-chan-snailien-gif-4988120458484741516',
        'https://tenor.com/view/meteorgirl-snail%27s-house-snailien-alien-pop-gif-3817028083927145578',
        'https://tenor.com/view/snailchan-flying-balloon-snail%27s-house-snails-house-gif-18370967392244891292',
        'https://tenor.com/view/supergirl-snail%27s-house-snail-chan-gif-12013102839060740840',
        'https://tenor.com/view/snails-house-gif-27013550'
    ]

    @slash_command(name='cucumber', description='Cucumber')
    async def cucumber(self, ctx: SlashContext):
        await ctx.send('https://cdn.discordapp.com/attachments/1181692967984046100/1191457105027272714/snail-cucumber-258532276.gif')

    @slash_command(name='silly', description='silly')
    async def silly(self, ctx: SlashContext):
        await ctx.send('https://cdn.discordapp.com/attachments/158964992756940800/1365625571664724009/moonrabbit4.gif?ex=68b2202c&is=68b0ceac&hm=f5c5b3471e7ba80cc6f4a66f3909dca5ea7e6de18884a8e2c0115591d20d0fa9&')

    @slash_command(description='snale')
    async def snale(self, ctx: SlashContext):
        await ctx.send(random.choice(self.snails))