from pyperbot.piping import PipeClosed, PipeError
from pyperbot.pyperparser import total
from pyperbot.wrappers import plugin, complexcommand


@plugin
class Xargs:
    # async def funcs_n_args(self, pipeline, initial, preargs=[]):
    #     # print("pipeline >>", pipeline)
    #     count = 0
    #     first = True
    #     for [cmd_name, *cmd_args] in pipeline:
    #         # if count > 50:
    #         #     raise toomany()
    #         if first:
    #             first = False
    #             args = cmd_args + (initial.data or [])
    #             # text = [str(t) for t in args.args[1:]]
    #         else:
    #             args = cmd_args
    #
    #         if cmd_name in self.bot.commands:
    #             func = self.bot.commands[cmd_name]
    #             yield (func, initial.to_args(args=args, line=" ".join(map(str, cmd_args))))
    #             count += 1
    #         elif cmd_name in self.bot.aliases:
    #             first = True
    #             async for func_, args_, text_, _ in self.bot.funcs_n_args(self.bot.aliases[cmd_name], initial,
    #                                                                       preargs=args, offset=0, count=count + 1):
    #                 # if first:
    #                 #     args_ += args
    #                 #     text_ += text
    #                 #     first = False
    #                 yield (func_, initial.to_args(args=args_, line=" ".join(text_)))
    #                 count += 1
    #         else:
    #             raise CommandNotDefined(0, cmd_name)

    @complexcommand
    async def xargs(self, args, inpipe, outpipe):
        """will call the pipeline for every passed in message, substituing !:: args"""
        try:
            strpipe = False
            if args.data and args.data[0] == '-s':
                strpipe = True
                pipeline = args.data[1]
            else:
                pipeline = args.text
            while 1:
                x = await inpipe.recv()
                if strpipe:
                    parse = total.parseString(pipeline, parseAll=True)
                    try:
                        await self.bot.run_parse(parse, x, callback=outpipe.send, preargs=x.data, recursion_limit=2)
                    except PipeError as e:
                        raise PipeError([(0, err) for loc, err in e.exs])
                else:
                    raise NotImplementedError("please use the -s option for now")
        except PipeClosed:
            pass
        finally:
            outpipe.close()
            inpipe.close()
