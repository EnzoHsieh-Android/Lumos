preflight-4: ran

# code-macrobench-20-iters r2 收貨

審材:主線 3175444b 到 e4b5dd54 的完整改動 r2-snapshot.patch(575 行),加修補差異 r2-repair.patch(f1c32a67 → e4b5dd54,385 行)。兩席全新:單審、架構對齊,都交回後才一起存檔。兩席都乾淨、0 條;單審自己跑 -k macrobench 197 條全過,並用溢位、平均 0、超大整數、次正規數實測過變異係數的修補。
修補因果:判過,這輪沒有上一輪修補造成的新問題。

折 0、放行 0、駁回 0。--regression-set none。
