#include <stdlib.h>
#include <stdio.h>


typedef struct{
    float x, y, w, h, score;
    int idx;
} box;


float overlap(float x1, float w1, float x2, float w2)
{
    float l1 = x1 - w1/2;
    float l2 = x2 - w2/2;
    float left = l1 > l2 ? l1 : l2;
    float r1 = x1 + w1/2;
    float r2 = x2 + w2/2;
    float right = r1 < r2 ? r1 : r2;
    return right - left;
}


float box_intersection(box a, box b)
{
    float w = overlap(a.x, a.w, b.x, b.w);
    float h = overlap(a.y, a.h, b.y, b.h);
    if(w < 0 || h < 0) return 0;
    float area = w*h;
    return area;
}


float box_union(box a, box b)
{
    float i = box_intersection(a, b);
    float u = a.w*a.h + b.w*b.h - i;
    return u;
}


float box_iou(box a, box b)
{
    return box_intersection(a, b)/box_union(a, b);
}


int comparator(const void *pa, const void *pb)
{
    const box* a = (const box*)pa;
    const box* b = (const box*)pb;
    float d = b->score - a->score;
    if (d > 0){
        return 1;
    } else if (d < 0){
        return -1;
    } else{
        return 0;
    }
}


void do_nms(box *boxes, int total, float thresh)
{
    qsort(boxes, total, sizeof(box), comparator);
    int i, j;
    for(i = 0; i < total; ++i){
        if (boxes[i].score == 0) continue;
        for(j = i+1; j < total; ++j){
            if (box_iou(boxes[i], boxes[j]) > thresh){
                boxes[j].score = 0;
            }
        }
    }
}


