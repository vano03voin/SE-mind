DISCORD_TOCKEN = 'lolkekcheburek' # dont forget to invite ur bot on ur server and give him rights
TIME_ZONE = [3, 'MSK']
OBSERVED = {  # support multiplie servers
    'C:/hard-serwer': {  # name of server is folder where is torch.exe
        'do_restarts': True,
        'restart_delay': 600,  # how far in advance to warn the players about the restart
        'do_server_use_depatch_savefix': False,  # not support True setting now. its in progress
        'restart_pram': {  # when and what program have to do restart
            2: [  # key is the hour in 24 day when restart should happen
                'fix_world',  # commands for world_manager what he have to do.
                'check_security',  # check what they do in managers/world_manager in class WorldManager
                'fix_world'
            ],
            10: [
                'fix_world'
            ]
        },
        'discord': {  # links to chanels with SE_bridge. (IMPORTANT)
            'sebd': 1072129212472893520,  # chanel with commands to serer
            'ingame_chat': 1056079199347150989  # chanel with ingame chat
        }
    }
}
