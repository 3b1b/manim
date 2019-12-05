
from manimlib.imports import *
from active_projects.eop.reusable_imports import *

class ShuffleThroughAllSequences(Scene):
    CONFIG = {
        "nb_coins" : 20,
        "run_time" : 5,
        "fps" : int(1.0/PRODUCTION_QUALITY_FRAME_DURATION),
        "coin_size" : 0.5,
        "coin_spacing" : 0.65
    }


    def construct(self):

        nb_frames = self.run_time * self.fps
        nb_relevant_coins = int(np.log2(nb_frames)) + 1
        print("relevant coins:", nb_relevant_coins)
        nb_idle_coins = self.nb_coins - nb_relevant_coins

        idle_heads = CoinSequence(nb_idle_coins * ["H"],
            radius = self.coin_size * 0.5,
            spacing = self.coin_spacing)
        idle_tails = CoinSequence(nb_idle_coins * ["T"],
            radius = self.coin_size * 0.5,
            spacing = self.coin_spacing)
        idle_tails.fade(0.5)

        idle_part = VGroup(idle_heads, idle_tails)
        left_idle_part = CoinSequence(6 * ["H"],
            radius = self.coin_size * 0.5,
            spacing = self.coin_spacing)

        #self.add(idle_part, left_idle_part)
        self.add(left_idle_part)
        last_coin_seq = VGroup()

        for i in range(2**nb_relevant_coins):
            binary_seq = binary(i)
            # pad to the left with 0s
            nb_leading_zeroes = nb_relevant_coins - len(binary_seq)
            for j in range(nb_leading_zeroes):
                binary_seq.insert(0, 0)
            seq2 = ["H" if x == 0 else "T" for x in binary_seq]
            coin_seq = CoinSequence(seq2,
                radius = self.coin_size * 0.5,
                spacing = self.coin_spacing)
            coin_seq.next_to(idle_part, LEFT, buff = self.coin_spacing - self.coin_size)
            left_idle_part.next_to(coin_seq, LEFT, buff = self.coin_spacing - self.coin_size)
            all_coins = VGroup(left_idle_part, coin_seq) #, idle_part)
            all_coins.center()
            self.remove(last_coin_seq)
            self.add(coin_seq)
            #self.wait(1.0/self.fps)
            self.update_frame()
            self.add_frames(self.get_frame())
            last_coin_seq = coin_seq
            print(float(i)/2**nb_relevant_coins)





